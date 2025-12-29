"""
Pre-flight validation checks before running evaluations.

This module ensures all prerequisites are met before starting expensive operations,
preventing wasted time, resources, and API costs.
"""

import os
import json
import subprocess
import requests
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from sfbench.utils.sfdx import verify_devhub, run_sfdx, parse_json_output


@dataclass
class PreflightResult:
    """Result of pre-flight checks."""
    passed: bool
    checks: Dict[str, Tuple[bool, str]]  # check_name -> (passed, message)
    warnings: List[str]
    errors: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "passed": self.passed,
            "checks": {k: {"passed": v[0], "message": v[1]} for k, v in self.checks.items()},
            "warnings": self.warnings,
            "errors": self.errors
        }


class PreflightValidator:
    """Validates prerequisites before running evaluations."""
    
    def __init__(self):
        self.checks = {}
        self.warnings = []
        self.errors = []
    
    def check_devhub_connectivity(self) -> Tuple[bool, str]:
        """Check DevHub authentication and connectivity."""
        try:
            result = verify_devhub()
            if result:
                return True, "DevHub authenticated and accessible"
            else:
                return False, "DevHub not authenticated or not found. Run 'sf org login web --alias <devhub-alias>'"
        except Exception as e:
            return False, f"DevHub check failed: {str(e)}"
    
    def check_scratch_org_limits(self, required_count: int) -> Tuple[bool, str, Optional[int]]:
        """
        Check available scratch org limits vs required.
        
        Returns:
            (has_enough, message, available_count)
        """
        try:
            # Get scratch org info
            exit_code, stdout, stderr = run_sfdx(
                "sf org list --json",
                timeout=30
            )
            
            if exit_code != 0:
                return False, f"Could not check scratch org limits: {stderr}", None
            
            data = parse_json_output(stdout)
            orgs = data.get('result', {}).get('nonScratchOrgs', [])
            
            # Find DevHub orgs
            devhub_orgs = [org for org in orgs if org.get('isDevHub', False)]
            
            if not devhub_orgs:
                return False, "No DevHub orgs found. Authenticate a DevHub first.", None
            
            # Try to get limit info (this might not be directly available via CLI)
            # We'll use a heuristic: try to create a test org to check limits
            # But for now, we'll just check if we can list orgs
            
            # For Enterprise Edition, typical limits are:
            # - Daily: 80 scratch orgs
            # - Active: 40 scratch orgs
            
            # Count active scratch orgs
            scratch_orgs = data.get('result', {}).get('scratchOrgs', [])
            active_count = len([org for org in scratch_orgs if org.get('status') == 'Active'])
            
            # Estimate available (conservative: assume 40 active limit for Enterprise)
            # In practice, we should query the org for actual limits
            estimated_daily_limit = 80  # Enterprise Edition default
            estimated_active_limit = 40
            
            available_daily = estimated_daily_limit  # We don't track daily usage easily
            available_active = estimated_active_limit - active_count
            
            if available_active < required_count:
                return False, f"Insufficient scratch org capacity. Need {required_count}, have ~{available_active} available (estimated {estimated_active_limit} active limit, {active_count} currently active)", available_active
            
            if active_count > estimated_active_limit * 0.8:
                return True, f"⚠️  Warning: {active_count}/{estimated_active_limit} scratch orgs active (80%+ capacity)", available_active
            
            return True, f"✅ Sufficient capacity: ~{available_active} scratch orgs available (estimated)", available_active
            
        except Exception as e:
            return False, f"Could not check scratch org limits: {str(e)}", None
    
    def check_llm_model(
        self, 
        model_name: str, 
        provider: str,
        api_key: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Check if LLM model is available and generates correct format.
        
        Returns:
            (is_valid, message)
        """
        try:
            # Determine API endpoint and headers based on provider
            if provider == "routellm":
                url = "https://routellm.abacus.ai/v1/chat/completions"
                api_key = api_key or os.getenv("ROUTELLM_API_KEY")
                if not api_key:
                    return False, "ROUTELLM_API_KEY not set"
                
                # First, check if model exists
                models_url = "https://routellm.abacus.ai/v1/models"
                try:
                    resp = requests.get(
                        models_url,
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=10
                    )
                    if resp.status_code == 200:
                        models_data = resp.json()
                        available_models = [m.get('id', '') for m in models_data.get('data', [])]
                        if model_name not in available_models:
                            return False, f"Model '{model_name}' not found in RouteLLM. Available: {', '.join(available_models[:5])}..."
                except Exception as e:
                    return False, f"Could not verify model availability: {str(e)}"
                
                # Test format generation
                test_payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert Salesforce developer. Generate solutions as unified diff patches.\n\nCRITICAL INSTRUCTIONS:\n1. Output ONLY the raw patch content, NO markdown code blocks\n2. Start directly with: diff --git a/path/to/file b/path/to/file\n3. Use proper unified diff format"
                        },
                        {
                            "role": "user",
                            "content": "Generate a simple git diff patch to add a comment '// Test' to a file force-app/main/default/classes/Test.cls"
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
                
                resp = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    },
                    json=test_payload,
                    timeout=30
                )
                
                if resp.status_code != 200:
                    error_data = resp.json() if resp.content else {}
                    error_msg = error_data.get('error', {}).get('message', f"HTTP {resp.status_code}")
                    return False, f"API call failed: {error_msg}"
                
                data = resp.json()
                if 'choices' not in data or not data['choices']:
                    return False, "Invalid API response format"
                
                content = data['choices'][0]['message']['content']
                
                # Check format
                has_diff_markers = (
                    content.strip().startswith('diff --git') or
                    '@@' in content or
                    ('---' in content and '+++' in content)
                )
                
                has_markdown = '```' in content
                
                if has_markdown and not has_diff_markers:
                    return False, "Model generates markdown blocks but not proper diff format"
                
                if not has_diff_markers:
                    return False, "Model does not generate proper git diff format"
                
                return True, f"✅ Model '{model_name}' available and generates valid diff format"
                
            elif provider == "openrouter":
                url = "https://openrouter.ai/api/v1/chat/completions"
                api_key = api_key or os.getenv("OPENROUTER_API_KEY")
                if not api_key:
                    return False, "OPENROUTER_API_KEY not set"
                
                # Check model availability
                models_url = "https://openrouter.ai/api/v1/models"
                try:
                    resp = requests.get(models_url, timeout=10)
                    if resp.status_code == 200:
                        models_data = resp.json()
                        available_models = [m.get('id', '') for m in models_data.get('data', [])]
                        if model_name not in available_models:
                            return False, f"Model '{model_name}' not found in OpenRouter. Available: {', '.join(available_models[:5])}..."
                except Exception as e:
                    return False, f"Could not verify model availability: {str(e)}"
                
                # Test format (similar to RouteLLM)
                test_payload = {
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are an expert Salesforce developer. Generate solutions as unified diff patches.\n\nCRITICAL INSTRUCTIONS:\n1. Output ONLY the raw patch content, NO markdown code blocks\n2. Start directly with: diff --git a/path/to/file b/path/to/file\n3. Use proper unified diff format"
                        },
                        {
                            "role": "user",
                            "content": "Generate a simple git diff patch to add a comment '// Test' to a file force-app/main/default/classes/Test.cls"
                        }
                    ],
                    "temperature": 0.1,
                    "max_tokens": 500
                }
                
                resp = requests.post(
                    url,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "HTTP-Referer": "https://github.com/yasarshaikh/SF-bench",
                        "Content-Type": "application/json"
                    },
                    json=test_payload,
                    timeout=30
                )
                
                if resp.status_code != 200:
                    error_data = resp.json() if resp.content else {}
                    error_msg = error_data.get('error', {}).get('message', f"HTTP {resp.status_code}")
                    return False, f"API call failed: {error_msg}"
                
                data = resp.json()
                if 'choices' not in data or not data['choices']:
                    return False, "Invalid API response format"
                
                content = data['choices'][0]['message']['content']
                
                # Check format
                has_diff_markers = (
                    content.strip().startswith('diff --git') or
                    '@@' in content or
                    ('---' in content and '+++' in content)
                )
                
                if not has_diff_markers:
                    return False, "Model does not generate proper git diff format"
                
                return True, f"✅ Model '{model_name}' available and generates valid diff format"
                
            elif provider in ["gemini", "google"]:
                api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
                if not api_key:
                    return False, "GOOGLE_API_KEY or GEMINI_API_KEY not set"
                
                # For Gemini, we'll do a simpler check
                # (Full format check would require google.generativeai import)
                return True, f"✅ Gemini API key configured (format check skipped for speed)"
                
            else:
                # For other providers, just check API key exists
                api_key_env = f"{provider.upper()}_API_KEY"
                api_key = api_key or os.getenv(api_key_env)
                if not api_key:
                    return False, f"{api_key_env} not set"
                
                return True, f"✅ {provider} API key configured"
                
        except requests.exceptions.Timeout:
            return False, "API request timed out"
        except requests.exceptions.RequestException as e:
            return False, f"API request failed: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error: {str(e)}"
    
    def check_api_keys(self, provider: str, model_name: str) -> Tuple[bool, str, Optional[str]]:
        """
        Check if required API keys are set.
        
        Returns:
            (has_key, message, api_key_value)
        """
        if provider == "routellm":
            api_key = os.getenv("ROUTELLM_API_KEY")
            if not api_key:
                return False, "ROUTELLM_API_KEY not set", None
            return True, "✅ ROUTELLM_API_KEY configured", api_key
        elif provider == "openrouter":
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                return False, "OPENROUTER_API_KEY not set", None
            return True, "✅ OPENROUTER_API_KEY configured", api_key
        elif provider in ["gemini", "google"]:
            api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
            if not api_key:
                return False, "GOOGLE_API_KEY or GEMINI_API_KEY not set", None
            return True, "✅ Google API key configured", api_key
        else:
            api_key_env = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(api_key_env)
            if not api_key:
                return False, f"{api_key_env} not set", None
            return True, f"✅ {api_key_env} configured", api_key
    
    def run_all_checks(
        self,
        model_name: str,
        provider: str,
        required_scratch_orgs: int = 1,
        skip_devhub: bool = False,
        skip_llm_check: bool = False
    ) -> PreflightResult:
        """
        Run all pre-flight checks.
        
        Args:
            model_name: LLM model name
            provider: AI provider
            required_scratch_orgs: Number of scratch orgs needed
            skip_devhub: Skip DevHub checks
            skip_llm_check: Skip LLM format validation (faster)
        
        Returns:
            PreflightResult with all check results
        """
        self.checks = {}
        self.warnings = []
        self.errors = []
        
        # 1. Check API keys
        has_key, key_msg, api_key = self.check_api_keys(provider, model_name)
        self.checks["api_key"] = (has_key, key_msg)
        if not has_key:
            self.errors.append(key_msg)
        
        # 2. Check DevHub (if not skipped)
        if not skip_devhub:
            devhub_ok, devhub_msg = self.check_devhub_connectivity()
            self.checks["devhub"] = (devhub_ok, devhub_msg)
            if not devhub_ok:
                self.errors.append(devhub_msg)
        else:
            self.checks["devhub"] = (True, "Skipped (--skip-devhub)")
            self.warnings.append("DevHub check skipped - scratch org creation may fail")
        
        # 3. Check scratch org limits (if DevHub is available)
        if not skip_devhub and self.checks.get("devhub", (False, ""))[0]:
            limit_ok, limit_msg, available = self.check_scratch_org_limits(required_scratch_orgs)
            self.checks["scratch_org_limits"] = (limit_ok, limit_msg)
            if not limit_ok:
                self.errors.append(limit_msg)
            elif "Warning" in limit_msg:
                self.warnings.append(limit_msg)
        else:
            self.checks["scratch_org_limits"] = (True, "Skipped (DevHub check failed or skipped)")
        
        # 4. Check LLM model availability and format (if not skipped)
        if not skip_llm_check and has_key:
            llm_ok, llm_msg = self.check_llm_model(model_name, provider, api_key)
            self.checks["llm_model"] = (llm_ok, llm_msg)
            if not llm_ok:
                self.errors.append(llm_msg)
        else:
            if skip_llm_check:
                self.checks["llm_model"] = (True, "Skipped (--skip-llm-check)")
            else:
                self.checks["llm_model"] = (False, "Skipped (API key not available)")
        
        # Determine overall result
        passed = len(self.errors) == 0
        
        return PreflightResult(
            passed=passed,
            checks=self.checks,
            warnings=self.warnings,
            errors=self.errors
        )


def interactive_prompt(question: str, default: Optional[str] = None, required: bool = True) -> str:
    """Interactive prompt for user input."""
    prompt = question
    if default:
        prompt += f" [{default}]"
    if not required:
        prompt += " (optional)"
    prompt += ": "
    
    while True:
        try:
            response = input(prompt).strip()
            if response:
                return response
            elif default:
                return default
            elif not required:
                return ""
            else:
                print("  ⚠️  This field is required. Please provide a value.")
        except KeyboardInterrupt:
            print("\n  ❌ Cancelled by user")
            raise


def interactive_setup() -> Dict[str, str]:
    """Interactive setup for missing configuration."""
    print("\n" + "=" * 70)
    print("🔧 INTERACTIVE SETUP")
    print("=" * 70)
    print("Some required configuration is missing. Let's set it up interactively.\n")
    
    config = {}
    
    # Check and prompt for API keys
    providers_to_check = [
        ("ROUTELLM_API_KEY", "RouteLLM API key"),
        ("OPENROUTER_API_KEY", "OpenRouter API key"),
        ("GOOGLE_API_KEY", "Google/Gemini API key"),
    ]
    
    for env_var, description in providers_to_check:
        if not os.getenv(env_var):
            print(f"\n📝 {description}")
            print(f"   Get your key from:")
            if "RouteLLM" in description:
                print("   https://routellm.abacus.ai")
            elif "OpenRouter" in description:
                print("   https://openrouter.ai")
            elif "Google" in description:
                print("   https://aistudio.google.com")
            
            value = interactive_prompt(f"   Enter {env_var}", required=False)
            if value:
                config[env_var] = value
                os.environ[env_var] = value
                print(f"   ✅ {env_var} set")
    
    # Check DevHub
    print("\n🔐 DevHub Authentication")
    devhub_ok, _ = PreflightValidator().check_devhub_connectivity()
    if not devhub_ok:
        print("   ⚠️  DevHub not authenticated")
        print("   To authenticate, run:")
        print("   sf org login web --alias <your-devhub-alias>")
        response = interactive_prompt("   Have you authenticated a DevHub? (yes/no)", default="no", required=False)
        if response.lower() == "yes":
            # Re-check
            devhub_ok, _ = PreflightValidator().check_devhub_connectivity()
            if not devhub_ok:
                print("   ⚠️  Still not detected. Please run 'sf org login web' and try again.")
        else:
            print("   ⚠️  You'll need to authenticate a DevHub before running evaluations.")
    
    print("\n✅ Interactive setup complete!")
    print("=" * 70)
    
    return config
