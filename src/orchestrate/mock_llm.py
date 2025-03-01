import asyncio
import random
from typing import Optional, Dict, Any, List

class MockLLMClient:
    """
    A mock LLM client for testing without requiring an actual OpenAI API key.
    
    This class simulates responses from an LLM with configurable delay and response patterns.
    """
    
    def __init__(self, delay_range: tuple = (0.5, 2.0)):
        """
        Initialize the mock LLM client.
        
        Args:
            delay_range: Tuple of (min_delay, max_delay) in seconds to simulate API latency
        """
        self.delay_range = delay_range
        
    async def generate(self, prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
        """
        Generate a mock completion for the given prompt.
        
        Args:
            prompt: The prompt to generate a completion for
            temperature: Controls randomness (ignored in mock)
            max_tokens: Maximum number of tokens to generate (ignored in mock)
            
        Returns:
            A mock generated text
        """
        # Simulate API delay
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)
        
        # Generate a mock response based on the prompt
        if "debate" in prompt.lower():
            return self._generate_debate_response(prompt)
        elif "dnd" in prompt.lower() or "dungeon" in prompt.lower():
            return self._generate_dnd_response(prompt)
        elif "market" in prompt.lower():
            return self._generate_marketing_response(prompt)
        else:
            return self._generate_generic_response(prompt)
    
    def _generate_debate_response(self, prompt: str) -> str:
        """Generate a mock debate response."""
        debate_responses = [
            "From a logical perspective, we must consider three key factors...",
            "The opposing argument fails to account for recent developments in...",
            "While I understand the counterpoint, the evidence clearly shows...",
            "This position is supported by multiple peer-reviewed studies that demonstrate...",
            "The historical precedent for this approach can be traced back to..."
        ]
        return random.choice(debate_responses)
    
    def _generate_dnd_response(self, prompt: str) -> str:
        """Generate a mock D&D response."""
        dnd_responses = [
            "The ancient forest of Eldrath stretches before you, its twisted trees reaching toward the darkening sky...",
            "The dwarf warrior Thorin Stonehammer stands firm, his battleaxe gleaming in the torchlight...",
            "A mysterious figure emerges from the shadows of the tavern, their face hidden beneath a tattered hood...",
            "The dragon's roar echoes through the cavern as flames illuminate the treasure hoard...",
            "The party finds themselves at a crossroads, with an ancient stone marker bearing cryptic runes..."
        ]
        return random.choice(dnd_responses)
    
    def _generate_marketing_response(self, prompt: str) -> str:
        """Generate a mock marketing response."""
        marketing_responses = [
            "Our revolutionary product combines cutting-edge technology with intuitive design...",
            "Target audience analysis reveals three key demographics that would benefit from...",
            "The campaign should focus on the unique value proposition of sustainability and efficiency...",
            "A multi-channel approach including social media, influencer partnerships, and targeted ads will...",
            "The brand messaging should emphasize reliability, innovation, and customer-centric values..."
        ]
        return random.choice(marketing_responses)
    
    def _generate_generic_response(self, prompt: str) -> str:
        """Generate a generic mock response."""
        # Extract keywords from the prompt
        words = prompt.split()
        keywords = [word for word in words if len(word) > 4]
        
        if not keywords:
            return "I've processed your request and have some thoughts to share on this topic."
        
        # Use a keyword in the response
        keyword = random.choice(keywords)
        templates = [
            f"Based on my analysis of {keyword}, I recommend the following approach...",
            f"When considering {keyword}, it's important to remember several key factors...",
            f"The concept of {keyword} can be understood through the following framework...",
            f"I've evaluated your question about {keyword} and can provide these insights...",
            f"Looking at {keyword} from multiple perspectives reveals interesting patterns..."
        ]
        
        return random.choice(templates)

# Singleton instance for convenience
_mock_client: Optional[MockLLMClient] = None

def get_mock_client(delay_range: tuple = (0.5, 2.0)) -> MockLLMClient:
    """
    Get or create the mock LLM client.
    
    Args:
        delay_range: Tuple of (min_delay, max_delay) in seconds to simulate API latency
        
    Returns:
        MockLLMClient instance
    """
    global _mock_client
    if _mock_client is None:
        _mock_client = MockLLMClient(delay_range=delay_range)
    return _mock_client

async def generate_mock_completion(prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> str:
    """
    Generate a mock completion for the given prompt.
    
    Args:
        prompt: The prompt to generate a completion for
        temperature: Controls randomness (ignored in mock)
        max_tokens: Maximum number of tokens to generate (ignored in mock)
        
    Returns:
        A mock generated text
    """
    client = get_mock_client()
    return await client.generate(prompt, temperature, max_tokens) 