"""
AI Agent integration for generating solutions to tasks.
Supports multiple AI providers including:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google Gemini (AI Studio)
- OpenRouter (access to 100+ models)
- Hugging Face
- Local models (Ollama, etc.)
"""
import json
import os
from typing import Optional, Dict, Any, List
from pathlib import Path
import requests


class AIAgentError(Exception):
    """Base exception for AI agent errors."""
    pass


class AIAgent:
    """
    Interface for AI code generation agents.
    
    Supports multiple providers for flexibility in model testing.
    """
    
    # Supported providers
    PROVIDERS = ["openai", "anthropic", "gemini", "google", "openrouter", "routellm", "huggingface", "local", "ollama"]
    
    def __init__(
        self, 
        provider: str = "openai", 
        model: str = "gpt-3.5-turbo", 
        api_key: Optional[str] = None,
        base_url: Optional[str] = None
    ):
        """
        Initialize AI agent.
        
        Args:
            provider: AI provider (openai, anthropic, gemini, openrouter, huggingface, local, ollama)
            model: Model name/identifier
            api_key: API key (if required)
            base_url: Custom base URL (for OpenRouter or self-hosted)
        """
        self.provider = provider.lower()
        self.model = model
        self.base_url = base_url
        
        # Resolve API key based on provider
        if api_key:
            self.api_key = api_key
        elif self.provider in ["gemini", "google"]:
            self.api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        elif self.provider == "openrouter":
            self.api_key = os.getenv("OPENROUTER_API_KEY")
        elif self.provider == "routellm":
            self.api_key = os.getenv("ROUTELLM_API_KEY")
        elif self.provider == "ollama":
            self.api_key = None  # Ollama doesn't need API key
        else:
            self.api_key = os.getenv(f"{provider.upper()}_API_KEY")
        
    def generate_solution(
        self,
        task_description: str,
        context: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Generate a solution (patch/diff) for a given task.
        
        Args:
            task_description: Description of the task/problem
            context: Additional context (task type, repo info, etc.)
            files: Relevant files with their contents
            
        Returns:
            Unified diff string (patch format)
        """
        generators = {
            "openai": self._generate_openai,
            "anthropic": self._generate_anthropic,
            "gemini": self._generate_gemini,
            "google": self._generate_gemini,
            "openrouter": self._generate_openrouter,
            "routellm": self._generate_routellm,
            "huggingface": self._generate_huggingface,
            "ollama": self._generate_ollama,
            "local": self._generate_local,
        }
        
        generator = generators.get(self.provider)
        if generator:
            return generator(task_description, context, files)
        else:
            raise AIAgentError(f"Unsupported provider: {self.provider}. Supported: {self.PROVIDERS}")
    
    def _generate_openai(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """Generate solution using OpenAI API."""
        try:
            import openai
            
            if not self.api_key:
                return self._generate_local(task_description, context, files)
            
            client = openai.OpenAI(api_key=self.api_key)
            
            prompt = self._build_prompt(task_description, context, files)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=8192
            )
            
            return self._clean_response(response.choices[0].message.content)
            
        except ImportError:
            return self._generate_local(task_description, context, files)
        except Exception as e:
            raise AIAgentError(f"OpenAI generation failed: {str(e)}")
    
    def _generate_anthropic(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """Generate solution using Anthropic Claude API."""
        try:
            import anthropic
            
            if not self.api_key:
                return self._generate_local(task_description, context, files)
            
            client = anthropic.Anthropic(api_key=self.api_key)
            
            prompt = self._build_prompt(task_description, context, files)
            
            message = client.messages.create(
                model=self.model,
                max_tokens=8192,
                temperature=0.1,
                system=self._get_system_prompt(),
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return self._clean_response(message.content[0].text)
            
        except ImportError:
            return self._generate_local(task_description, context, files)
        except Exception as e:
            raise AIAgentError(f"Anthropic generation failed: {str(e)}")
    
    def _generate_gemini(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """Generate solution using Google Gemini API (AI Studio)."""
        try:
            import google.generativeai as genai
            
            if not self.api_key:
                return self._generate_local(task_description, context, files)
            
            genai.configure(api_key=self.api_key)
            
            model_name = self.model if self.model else "gemini-2.5-flash"
            if model_name.startswith("models/"):
                model_name = model_name.replace("models/", "")
            
            model = genai.GenerativeModel(model_name)
            
            prompt = self._build_prompt(task_description, context, files)
            full_prompt = f"{self._get_system_prompt()}\n\n{prompt}"
            
            response = model.generate_content(
                full_prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 16384,
                }
            )
            
            return self._clean_response(response.text)
            
        except ImportError:
            raise AIAgentError("google-generativeai package not installed. Install with: pip install google-generativeai")
        except Exception as e:
            raise AIAgentError(f"Gemini generation failed: {str(e)}")
    
    def _generate_openrouter(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """
        Generate solution using OpenRouter API.
        
        OpenRouter provides unified access to 100+ models including:
        - Claude 3.5 Sonnet
        - GPT-4 Turbo
        - Llama 3.1
        - Mistral Large
        - And many more
        
        See: https://openrouter.ai/docs
        """
        if not self.api_key:
            raise AIAgentError("OpenRouter API key required. Set OPENROUTER_API_KEY environment variable.")
        
        try:
            prompt = self._build_prompt(task_description, context, files)
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/yasarshaikh/SF-bench",
                "X-Title": "SF-Bench"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 6000  # Reduced for free tier compatibility
            }
            
            response = requests.post(
                self.base_url or "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return self._clean_response(result["choices"][0]["message"]["content"])
            else:
                error_msg = response.json().get("error", {}).get("message", response.text)
                raise AIAgentError(f"OpenRouter API error: {error_msg}")
                
        except requests.exceptions.Timeout:
            raise AIAgentError("OpenRouter request timed out after 120 seconds")
        except Exception as e:
            if "AIAgentError" in str(type(e)):
                raise
            raise AIAgentError(f"OpenRouter generation failed: {str(e)}")
    
    def _generate_routellm(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """
        Generate solution using RouteLLM API.
        
        RouteLLM follows OpenAI Chat Completions API spec.
        Supports models like Grok 4.1 Fast, GPT-5, etc.
        
        See: https://routellm.abacus.ai
        """
        if not self.api_key:
            raise AIAgentError("RouteLLM API key required. Set ROUTELLM_API_KEY environment variable.")
        
        try:
            prompt = self._build_prompt(task_description, context, files)
            
            url = self.base_url or "https://routellm.abacus.ai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": self._get_system_prompt()},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.1,
                "max_tokens": 8192,
                "stream": False
            }
            
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, dict) and "choices" in result:
                    return self._clean_response(result["choices"][0]["message"]["content"])
                else:
                    raise AIAgentError(f"RouteLLM API returned unexpected response format: {result}")
            else:
                # Handle error response
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_msg = error_data.get("error", {}).get("message", response.text) if isinstance(error_data.get("error"), dict) else str(error_data)
                    else:
                        error_msg = str(error_data)
                except:
                    error_msg = response.text or f"HTTP {response.status_code}"
                raise AIAgentError(f"RouteLLM API error ({response.status_code}): {error_msg}")
                
        except requests.exceptions.Timeout:
            raise AIAgentError("RouteLLM request timed out after 120 seconds")
        except Exception as e:
            if "AIAgentError" in str(type(e)):
                raise
            raise AIAgentError(f"RouteLLM generation failed: {str(e)}")
    
    def _generate_ollama(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """
        Generate solution using local Ollama instance.
        
        Requires Ollama running locally: https://ollama.ai
        """
        try:
            prompt = self._build_prompt(task_description, context, files)
            
            base_url = self.base_url or "http://localhost:11434"
            
            response = requests.post(
                f"{base_url}/api/generate",
                json={
                    "model": self.model or "codellama",
                    "prompt": f"{self._get_system_prompt()}\n\n{prompt}",
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 8192
                    }
                },
                timeout=300
            )
            
            if response.status_code == 200:
                return self._clean_response(response.json()["response"])
            else:
                raise AIAgentError(f"Ollama error: {response.text}")
                
        except requests.exceptions.ConnectionError:
            raise AIAgentError("Ollama not running. Start with: ollama serve")
        except Exception as e:
            raise AIAgentError(f"Ollama generation failed: {str(e)}")
    
    def _generate_huggingface(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """Generate solution using Hugging Face Inference API."""
        try:
            if not self.api_key:
                return self._generate_local(task_description, context, files)
            
            prompt = self._build_prompt(task_description, context, files)
            
            api_url = f"https://api-inference.huggingface.co/models/{self.model}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_length": 4000}},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return self._clean_response(result[0].get("generated_text", ""))
            
            return self._generate_local(task_description, context, files)
            
        except Exception as e:
            return self._generate_local(task_description, context, files)
    
    def _generate_local(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """
        Fallback for when no AI provider is available.
        Returns a template for manual completion.
        """
        return f"""# Solution Template (No AI Provider Available)
# Task: {task_description}
# 
# To use an AI provider, set one of:
# - OPENAI_API_KEY
# - ANTHROPIC_API_KEY
# - GOOGLE_API_KEY or GEMINI_API_KEY
# - OPENROUTER_API_KEY
# 
# Or use Ollama locally: ollama serve
#
# Expected format: Unified diff patch
# 
# diff --git a/path/to/file b/path/to/file
# index 1234567..abcdefg 100644
# --- a/path/to/file
# +++ b/path/to/file
# @@ -10,6 +10,7 @@
#      // Existing code
# +    // Your solution here
#      // More code
"""
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt for AI models."""
        return """You are an expert Salesforce developer. Generate solutions as unified diff patches.

CRITICAL INSTRUCTIONS:
1. Output ONLY the raw patch content, NO markdown code blocks (no ```diff or ```)
2. Start directly with: diff --git a/path/to/file b/path/to/file
3. Include COMPLETE file changes - do not truncate
4. Use proper unified diff format with context lines
5. The patch must apply cleanly with 'git apply'"""
    
    def _build_prompt(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """Build the prompt for AI generation."""
        prompt_parts = [
            "Task Description:",
            task_description,
            "\n"
        ]
        
        if context:
            prompt_parts.append("Context:")
            prompt_parts.append(json.dumps(context, indent=2))
            prompt_parts.append("\n")
        
        if files:
            prompt_parts.append("Relevant Files:")
            for file_path, content in files.items():
                prompt_parts.append(f"\n--- {file_path} ---")
                prompt_parts.append(content[:3000])  # Limit file content
            prompt_parts.append("\n")
        
        prompt_parts.append(
            "\nGenerate a COMPLETE unified diff patch that solves this task. "
            "The patch MUST be in standard git diff format and ready to apply with 'git apply'. "
            "Include ALL file changes needed. Do not truncate."
        )
        
        return "\n".join(prompt_parts)

    def _clean_response(self, response: str) -> str:
        """Clean the AI response, removing markdown code blocks and fixing common issues."""
        result = response.strip()
        
        # Remove markdown code blocks
        if "```" in result:
            lines = result.split("\n")
            cleaned_lines = []
            skip_until_end = False
            for line in lines:
                if line.strip().startswith("```"):
                    if "diff" in line.lower() or "patch" in line.lower():
                        skip_until_end = True
                        continue
                    elif skip_until_end:
                        skip_until_end = False
                        continue
                if not skip_until_end:
                    cleaned_lines.append(line)
            result = "\n".join(cleaned_lines)
        
        # Remove any leading/trailing non-diff content
        lines = result.split("\n")
        diff_start = -1
        for i, line in enumerate(lines):
            if line.startswith("diff --git") or line.startswith("---"):
                diff_start = i
                break
        
        if diff_start > 0:
            result = "\n".join(lines[diff_start:])
        
        return result.strip()


# Convenience functions for common providers

def create_openai_agent(model: str = "gpt-4-turbo", api_key: Optional[str] = None) -> AIAgent:
    """Create an OpenAI agent."""
    return AIAgent(provider="openai", model=model, api_key=api_key)


def create_anthropic_agent(model: str = "claude-3-5-sonnet-20241022", api_key: Optional[str] = None) -> AIAgent:
    """Create an Anthropic Claude agent."""
    return AIAgent(provider="anthropic", model=model, api_key=api_key)


def create_gemini_agent(model: str = "gemini-2.5-flash", api_key: Optional[str] = None) -> AIAgent:
    """Create a Google Gemini agent."""
    return AIAgent(provider="gemini", model=model, api_key=api_key)


def create_openrouter_agent(model: str = "anthropic/claude-3.5-sonnet", api_key: Optional[str] = None) -> AIAgent:
    """
    Create an OpenRouter agent.
    
    Popular models:
    - anthropic/claude-3.5-sonnet
    - openai/gpt-4-turbo
    - meta-llama/llama-3.1-405b-instruct
    - mistralai/mistral-large
    - google/gemini-pro-1.5
    
    See full list: https://openrouter.ai/models
    """
    return AIAgent(provider="openrouter", model=model, api_key=api_key)


def create_routellm_agent(model: str = "grok-4-1-fast-non-reasoning", api_key: Optional[str] = None) -> AIAgent:
    """
    Create a RouteLLM agent.
    
    Popular models (cheapest to most expensive):
    - grok-4-1-fast-non-reasoning (cheapest for full runs: $0.2/$0.5 per 1M tokens)
    - grok-4-fast-non-reasoning
    - gpt-5-nano ($0.05/$0.4 per 1M tokens)
    - gpt-5 ($1.25/$10 per 1M tokens)
    - claude-sonnet-4-5-20250929 ($3/$15 per 1M tokens)
    
    See: https://routellm.abacus.ai
    """
    # Map user-friendly names to actual model IDs
    model_map = {
        "grok-4.1-fast": "grok-4-1-fast-non-reasoning",
        "grok-4.1": "grok-4-1-fast-non-reasoning",
        "grok-4-fast": "grok-4-fast-non-reasoning",
    }
    actual_model = model_map.get(model.lower(), model)
    return AIAgent(provider="routellm", model=actual_model, api_key=api_key)


def create_ollama_agent(model: str = "codellama", base_url: str = "http://localhost:11434") -> AIAgent:
    """
    Create a local Ollama agent.
    
    Popular models:
    - codellama
    - deepseek-coder
    - qwen2.5-coder
    - llama3.1
    
    Requires Ollama running: https://ollama.ai
    """
    return AIAgent(provider="ollama", model=model, base_url=base_url)


def list_openrouter_models(api_key: Optional[str] = None) -> List[Dict]:
    """
    List available models from OpenRouter.
    
    Returns list of models with pricing and capabilities.
    """
    key = api_key or os.getenv("OPENROUTER_API_KEY")
    if not key:
        raise AIAgentError("OpenRouter API key required")
    
    response = requests.get(
        "https://openrouter.ai/api/v1/models",
        headers={"Authorization": f"Bearer {key}"}
    )
    
    if response.status_code == 200:
        return response.json().get("data", [])
    else:
        raise AIAgentError(f"Failed to fetch models: {response.text}")
