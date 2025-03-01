"""
Test the OpenAI client integration.

This test verifies that the OpenAI client can generate completions.
It requires a valid OpenAI API key in the environment.
"""

import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Skip tests if OPENAI_API_KEY is not set
pytestmark = [
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    ),
    pytest.mark.asyncio
]

async def test_generate_completion():
    """Test that the OpenAI client can generate completions."""
    from orchestrate.llm import generate_completion
    
    # Generate a completion
    result = await generate_completion(
        prompt="What is the capital of France?",
        temperature=0.7
    )
    
    # Check that we got a non-empty result
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Check that the result contains "Paris" (case insensitive)
    assert "paris" in result.lower()
    
async def test_llm_client_class():
    """Test that the LLMClient class can generate completions."""
    from orchestrate.llm import LLMClient
    
    # Create a client
    client = LLMClient()
    
    # Generate a completion
    result = await client.generate(
        prompt="What is the capital of Italy?",
        temperature=0.7
    )
    
    # Check that we got a non-empty result
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Check that the result contains "Rome" (case insensitive)
    assert "rome" in result.lower() 