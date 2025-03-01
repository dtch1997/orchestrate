"""
OpenAI client implementation for Orchestrate.

This module provides functions to interact with OpenAI's API for generating completions
using GPT models. It uses environment variables for API key configuration.
"""

import os
import asyncio
from typing import Optional, Dict, Any, List, Protocol
from openai import AsyncOpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Default model to use - check environment variable first, fallback to gpt-4o
DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")

class LLMClientProtocol(Protocol):
    """Protocol defining the interface for LLM clients."""
    
    async def generate(self, 
                      prompt: str, 
                      temperature: float = 0.7, 
                      max_tokens: Optional[int] = None,
                      system_message: str = "You are a helpful assistant.") -> str:
        """Generate a completion for the given prompt."""
        ...
    
    async def generate_structured(self,
                                prompt: str,
                                output_schema: Dict[str, Any],
                                temperature: float = 0.7,
                                max_tokens: Optional[int] = None,
                                system_message: str = "You are a helpful assistant.") -> Dict[str, Any]:
        """Generate a structured completion for the given prompt and schema."""
        ...

class OpenAIClient:
    """
    A lightweight wrapper around the OpenAI async client.
    
    This class provides a simple interface for making async calls to the OpenAI API.
    """
    
    def __init__(self, api_key: Optional[str] = None, model: str = DEFAULT_MODEL):
        """
        Initialize the LLM client.
        
        Args:
            api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY environment variable.
            model: The model to use for completions. Defaults to GPT-4o.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is required. Provide it as an argument or set OPENAI_API_KEY environment variable.")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
        self.model = model
    
    async def generate(self, 
                      prompt: str, 
                      temperature: float = 0.7, 
                      max_tokens: Optional[int] = None,
                      system_message: str = "You are a helpful assistant.") -> str:
        """
        Generate a completion for the given prompt.
        
        Args:
            prompt: The prompt to generate a completion for
            temperature: Controls randomness. Higher values (e.g., 0.8) make output more random, 
                         lower values (e.g., 0.2) make it more deterministic.
            max_tokens: Maximum number of tokens to generate
            system_message: System message to set the context
            
        Returns:
            The generated text
        """
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            # For MVP, just return the error as the response
            return f"Error generating completion: {str(e)}"
    
    async def generate_structured(self,
                                prompt: str,
                                output_schema: Dict[str, Any],
                                temperature: float = 0.7,
                                max_tokens: Optional[int] = None,
                                system_message: str = "You are a helpful assistant.") -> Dict[str, Any]:
        """
        Generate a structured completion for the given prompt and schema.
        
        Args:
            prompt: The prompt to generate a completion for
            output_schema: JSON schema defining the structure of the expected output
            temperature: Controls randomness. Higher values make output more random,
                         lower values make it more deterministic.
            max_tokens: Maximum number of tokens to generate
            system_message: System message to set the context
            
        Returns:
            The generated structured output as a dictionary
        """
        try:
            # Ensure the prompt mentions JSON to avoid API errors
            if "json" not in prompt.lower():
                prompt = f"{prompt} Return the result as JSON."
                
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "structured_output",
                        "schema": output_schema
                    }
                }
            )
            
            # Parse the JSON content
            import json
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            # For MVP, return an error dictionary
            return {"error": f"Error generating structured completion: {str(e)}"}

# Factory function to get the appropriate LLM client
def get_llm_client(use_mock: Optional[bool] = None, api_key: Optional[str] = None, model: str = DEFAULT_MODEL) -> LLMClientProtocol:
    """
    Factory function to get the appropriate LLM client based on configuration.
    
    Args:
        use_mock: Whether to use the mock client. If None, will check ORCHESTRATE_USE_MOCK env var.
        api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY environment variable.
        model: The model to use for completions. Defaults to GPT-4o.
        
    Returns:
        An LLM client instance (either real or mock)
    """
    # Determine whether to use mock
    if use_mock is None:
        use_mock = os.getenv("ORCHESTRATE_USE_MOCK", "false").lower() == "true"
    
    if use_mock:
        # Import here to avoid circular imports
        from orchestrate.mock_llm import MockLLMClient
        return MockLLMClient()
    else:
        return OpenAIClient(api_key=api_key, model=model)

# Singleton instance for convenience
_default_client: Optional[LLMClientProtocol] = None

def get_default_client(use_mock: Optional[bool] = None, api_key: Optional[str] = None, model: str = DEFAULT_MODEL) -> LLMClientProtocol:
    """
    Get or create the default LLM client.
    
    Args:
        use_mock: Whether to use the mock client. If None, will check ORCHESTRATE_USE_MOCK env var.
        api_key: OpenAI API key. If not provided, will look for OPENAI_API_KEY environment variable.
        model: The model to use for completions. Defaults to GPT-4o.
        
    Returns:
        LLMClient instance
    """
    global _default_client
    if _default_client is None:
        _default_client = get_llm_client(use_mock=use_mock, api_key=api_key, model=model)
    return _default_client

async def generate_completion(
    prompt: str, 
    temperature: float = 0.7, 
    max_tokens: Optional[int] = None,
    system_message: str = "You are a helpful assistant."
) -> str:
    """
    Generate a completion for the given prompt using the default client.
    
    Args:
        prompt: The prompt to generate a completion for
        temperature: Controls randomness
        max_tokens: Maximum number of tokens to generate
        system_message: System message to set the context
        
    Returns:
        The generated text
    """
    client = get_default_client()
    return await client.generate(prompt, temperature, max_tokens, system_message)

async def generate_structured_completion(
    prompt: str,
    output_schema: Dict[str, Any],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    system_message: str = "You are a helpful assistant."
) -> Dict[str, Any]:
    """
    Generate a structured completion for the given prompt using the default client.
    
    Args:
        prompt: The prompt to generate a completion for
        output_schema: JSON schema defining the structure of the expected output
        temperature: Controls randomness
        max_tokens: Maximum number of tokens to generate
        system_message: System message to set the context
        
    Returns:
        The generated structured output as a dictionary
    """
    client = get_default_client()
    return await client.generate_structured(prompt, output_schema, temperature, max_tokens, system_message) 