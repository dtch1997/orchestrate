"""
Test the OpenAI client integration.

This test verifies that the OpenAI client can generate completions.
It requires a valid OpenAI API key in the environment.
"""

import os
import unittest
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Skip tests if OPENAI_API_KEY is not set
SKIP_OPENAI_TESTS = not os.getenv("OPENAI_API_KEY")

class TestOpenAIClient(unittest.TestCase):
    """Test the OpenAI client integration."""
    
    @unittest.skipIf(SKIP_OPENAI_TESTS, "OPENAI_API_KEY not set")
    def test_generate_completion(self):
        """Test that the OpenAI client can generate completions."""
        from orchestrate.llm import generate_completion
        
        # Run the async function in the event loop
        result = asyncio.run(generate_completion(
            prompt="What is the capital of France?",
            temperature=0.7
        ))
        
        # Check that we got a non-empty result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that the result contains "Paris" (case insensitive)
        self.assertIn("paris", result.lower())
        
    @unittest.skipIf(SKIP_OPENAI_TESTS, "OPENAI_API_KEY not set")
    def test_llm_client_class(self):
        """Test that the LLMClient class can generate completions."""
        from orchestrate.llm import LLMClient
        
        # Create a client
        client = LLMClient()
        
        # Run the async function in the event loop
        result = asyncio.run(client.generate(
            prompt="What is the capital of Italy?",
            temperature=0.7
        ))
        
        # Check that we got a non-empty result
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
        
        # Check that the result contains "Rome" (case insensitive)
        self.assertIn("rome", result.lower())

if __name__ == "__main__":
    unittest.main() 