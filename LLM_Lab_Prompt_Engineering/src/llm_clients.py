"""
LLM Clients Module
Provides unified interface for interacting with LLM APIs.
"""

import os
import time
from typing import Dict, Any, Optional
from pathlib import Path
import yaml

# Load .env file if it exists
def load_env_file():
    """Load environment variables from .env file."""
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

load_env_file()

# Google Gemini
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


def load_config(config_path: str = "config/experiment_config.yaml") -> Dict[str, Any]:
    """Load experiment configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


class GeminiClient:
    """Wrapper for Google Gemini API."""
    
    def __init__(self, model_name: str = "gemini-1.5-flash", **kwargs):
        if not GEMINI_AVAILABLE:
            raise ImportError("google-generativeai package not installed")
        
        api_key = os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable not set")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        self.generation_config = genai.GenerationConfig(**kwargs)
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """
        Generate response from the model.
        
        Returns:
            Dict with 'response', 'token_count', 'latency_ms'
        """
        start_time = time.time()
        
        response = self.model.generate_content(
            prompt,
            generation_config=self.generation_config
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Extract response text and metadata
        response_text = response.text if response.text else ""
        
        # Estimate token count (rough approximation)
        token_count = len(response_text.split()) * 1.3  # Rough estimate
        
        return {
            "response": response_text,
            "token_count": int(token_count),
            "latency_ms": round(latency_ms, 2),
            "model": self.model_name,
            "finish_reason": "completed"
        }


class LLMClient:
    """Unified interface for multiple LLM providers."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize client based on configuration."""
        model_config = config['models']['primary']
        provider = model_config['provider']
        model_name = model_config['name']
        params = model_config.get('parameters', {})
        
        if provider == "google":
            self.client = GeminiClient(
                model_name=model_name,
                temperature=params.get('temperature', 0.7),
                top_p=params.get('top_p', 0.95),
                max_output_tokens=params.get('max_output_tokens', 1024)
            )
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        self.provider = provider
        self.model_name = model_name
    
    def generate(self, prompt: str) -> Dict[str, Any]:
        """Generate response using the configured model."""
        return self.client.generate(prompt)
    
    def get_model_info(self) -> Dict[str, str]:
        """Return model identification info."""
        return {
            "provider": self.provider,
            "model": self.model_name
        }


# Convenience function for quick testing
def quick_test():
    """Quick test to verify API connection."""
    config = load_config()
    client = LLMClient(config)
    
    print(f"Testing {client.get_model_info()}")
    result = client.generate("Say 'Hello, World!' in exactly 3 words.")
    print(f"Response: {result['response']}")
    print(f"Latency: {result['latency_ms']}ms")
    return result


if __name__ == "__main__":
    quick_test()
