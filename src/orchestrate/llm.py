import os
import asyncio
from typing import Optional, Dict, Any, List
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class LLMClient:
    """
    A lightweight wrapper around the OpenAI async client.
    
    This class provides a simple interface for making async calls to the OpenAI API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        """
        Initialize the LLM client.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY environment variable.
            model: The model to use for completions. Defaults to "gpt-3.5-turbo".
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Provide it as an argument or set OPENAI_API_KEY environment variable.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
    
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The prompt to generate a completion for
            temperature: Controls randomness. Higher values (e.g., 0.8) make output more random, 
                         lower values (e.g., 0.2) make it more deterministic.
            max_tokens: Maximum number of tokens to generate
            
        Returns:
            The generated text
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Error generating completion: {str(e)}")

# Singleton instance for convenience
_default_client: Optional[LLMClient] = None

def get_default_client(api_key: Optional[str] = None, model: str = "gpt-3.5-turbo") -> LLMClient:
    """
    Get or create the default LLM client.
    
    Args:
        api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY environment variable.
        model: The model to use for completions. Defaults to "gpt-3.5-turbo".
        
    Returns:
        LLMClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = LLMClient(api_key=api_key, model=model)
    return _default_client

async def generate_completion(prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """
    Generate a completion for the given prompt using the default client.
    
    Args:
        prompt: The prompt to generate a completion for
        temperature: Controls randomness
        max_tokens: Maximum number of tokens to generate
        
    Returns:
        The generated text
    """
    client = get_default_client()
    return await client.generate(prompt, temperature, max_tokens) 