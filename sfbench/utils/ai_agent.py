"""
AI Agent integration for generating solutions to tasks.
Supports multiple AI providers including free tiers.
"""
import json
import os
from typing import Optional, Dict, Any
from pathlib import Path
import requests
import subprocess


class AIAgentError(Exception):
    """Base exception for AI agent errors."""
    pass


class AIAgent:
    """Interface for AI code generation agents."""
    
    def __init__(self, provider: str = "openai", model: str = "gpt-3.5-turbo", api_key: Optional[str] = None):
        """
        Initialize AI agent.
        
        Args:
            provider: AI provider ("openai", "anthropic", "local", "huggingface")
            model: Model name/identifier
            api_key: API key (if required)
        """
        self.provider = provider.lower()
        self.model = model
        self.api_key = api_key or os.getenv(f"{provider.upper()}_API_KEY")
        
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
        if self.provider == "openai":
            return self._generate_openai(task_description, context, files)
        elif self.provider == "anthropic":
            return self._generate_anthropic(task_description, context, files)
        elif self.provider == "local":
            return self._generate_local(task_description, context, files)
        elif self.provider == "huggingface":
            return self._generate_huggingface(task_description, context, files)
        else:
            raise AIAgentError(f"Unsupported provider: {self.provider}")
    
    def _generate_openai(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """Generate solution using OpenAI API."""
        try:
            import openai
            
            if not self.api_key:
                # Try to use free tier or local fallback
                return self._generate_local(task_description, context, files)
            
            client = openai.OpenAI(api_key=self.api_key)
            
            prompt = self._build_prompt(task_description, context, files)
            
            response = client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Salesforce developer. Generate solutions as unified diff patches."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
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
                max_tokens=4000,
                temperature=0.1,
                system="You are an expert Salesforce developer. Generate solutions as unified diff patches.",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return message.content[0].text
            
        except ImportError:
            return self._generate_local(task_description, context, files)
        except Exception as e:
            raise AIAgentError(f"Anthropic generation failed: {str(e)}")
    
    def _generate_local(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """
        Generate solution using local model or fallback.
        For now, returns a placeholder that indicates manual review needed.
        """
        # This is a placeholder - in production, you'd integrate with:
        # - Ollama (local LLM)
        # - Hugging Face Transformers
        # - Or return a template for manual completion
        
        prompt = self._build_prompt(task_description, context, files)
        
        # Return a template patch that needs to be filled
        return f"""# AI-Generated Solution (Placeholder)
# Task: {task_description}
# 
# NOTE: This is a placeholder. In production, integrate with:
# - Ollama for local models
# - Hugging Face for open models
# - Or use API-based providers
#
# Expected format: Unified diff patch
# 
# diff --git a/path/to/file b/path/to/file
# index 1234567..abcdefg 100644
# --- a/path/to/file
# +++ b/path/to/file
# @@ -10,6 +10,7 @@
#      // Existing code
# +    // AI-generated solution
#      // More code
"""
    
    def _generate_huggingface(self, task_description: str, context: Optional[Dict], files: Optional[Dict]) -> str:
        """Generate solution using Hugging Face Inference API."""
        try:
            if not self.api_key:
                return self._generate_local(task_description, context, files)
            
            prompt = self._build_prompt(task_description, context, files)
            
            # Hugging Face Inference API
            api_url = f"https://api-inference.huggingface.co/models/{self.model}"
            headers = {"Authorization": f"Bearer {self.api_key}"}
            
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": prompt, "parameters": {"max_length": 2000}}
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
            
            return self._generate_local(task_description, context, files)
            
        except Exception as e:
            return self._generate_local(task_description, context, files)
    
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
                prompt_parts.append(content[:2000])  # Limit file content
            prompt_parts.append("\n")
        
        prompt_parts.append(
            "\nGenerate a unified diff patch that solves this task. "
            "The patch should be in standard git diff format and ready to apply with 'git apply'."
        )
        
        return "\n".join(prompt_parts)


class FreeTierAIAgent:
    """
    Wrapper for free-tier AI services.
    Supports: Hugging Face (free tier), local models, or manual templates.
    """
    
    @staticmethod
    def create_agent(provider: str = "huggingface") -> AIAgent:
        """
        Create an AI agent using free-tier services.
        
        Args:
            provider: "huggingface", "local", or "template"
        """
        if provider == "huggingface":
            # Hugging Face free tier - no API key needed for some models
            return AIAgent(provider="huggingface", model="bigcode/starcoder")
        elif provider == "local":
            return AIAgent(provider="local", model="local")
        else:
            # Template-based (for testing without actual AI)
            return AIAgent(provider="local", model="template")


def test_ai_agent(task_description: str, provider: str = "local") -> str:
    """
    Test AI agent with a sample task.
    
    Args:
        task_description: Task to solve
        provider: AI provider to use
        
    Returns:
        Generated solution (patch)
    """
    agent = FreeTierAIAgent.create_agent(provider)
    return agent.generate_solution(task_description)

