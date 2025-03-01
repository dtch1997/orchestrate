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
        
    async def generate(self, 
                      prompt: str, 
                      temperature: float = 0.7, 
                      max_tokens: Optional[int] = None,
                      system_message: str = "You are a helpful assistant.") -> str:
        """
        Generate a mock completion for the given prompt.
        
        Args:
            prompt: The prompt to generate a completion for
            temperature: Controls randomness (ignored in mock)
            max_tokens: Maximum number of tokens to generate (ignored in mock)
            system_message: System message to set the context (ignored in mock)
            
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
        elif "riddle" in prompt.lower():
            return self._generate_riddle_response(prompt)
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
    
    def _generate_riddle_response(self, prompt: str) -> str:
        """Generate a mock riddle response."""
        riddle_responses = [
            "What is always in front of you but can't be seen?",
            "What has a heart that doesn't beat?",
            "What is full of holes but still holds water?",
            "What is always in the middle of you but outside of you?",
            "What is always in your mouth but never in your stomach?"
        ]
        return random.choice(riddle_responses)
    
    def _generate_generic_response(self, prompt: str) -> str:
        """Generate a generic mock response."""
        # Extract keywords from the prompt
        keywords = [word for word in prompt.lower().split() if len(word) > 4]
        
        if keywords:
            return f"Based on your interest in {', '.join(keywords[:3])}, I would recommend exploring this topic further..."
        else:
            return "I understand your question. Here's a helpful response that addresses your needs..."
    
    async def generate_structured(self,
                                prompt: str,
                                output_schema: Dict[str, Any],
                                temperature: float = 0.7,
                                max_tokens: Optional[int] = None,
                                system_message: str = "You are a helpful assistant.") -> Dict[str, Any]:
        """
        Generate a mock structured completion for the given prompt and schema.
        
        Args:
            prompt: The prompt to generate a completion for
            output_schema: JSON schema defining the structure of the expected output
            temperature: Controls randomness (ignored in mock)
            max_tokens: Maximum number of tokens to generate (ignored in mock)
            system_message: System message to set the context (ignored in mock)
            
        Returns:
            A mock structured output as a dictionary
        """
        # Simulate API delay
        delay = random.uniform(*self.delay_range)
        await asyncio.sleep(delay)
        
        # Create a mock structured response based on the schema
        result = {}
        
        # Extract properties from the schema
        if 'properties' in output_schema:
            properties = output_schema['properties']
            for prop_name, prop_schema in properties.items():
                # Generate appropriate mock data based on property type
                prop_type = prop_schema.get('type', 'string')
                
                if prop_type == 'string':
                    if 'debate' in prompt.lower() and prop_name in ['debate_topic', 'pro_position', 'con_position']:
                        result[prop_name] = self._generate_debate_response(prompt)
                    elif ('dnd' in prompt.lower() or 'dungeon' in prompt.lower()) and prop_name in ['world_setting', 'character_details']:
                        result[prop_name] = self._generate_dnd_response(prompt)
                    elif 'market' in prompt.lower() and prop_name in ['product_name', 'key_features', 'target_audience']:
                        result[prop_name] = self._generate_marketing_response(prompt)
                    else:
                        result[prop_name] = f"Mock {prop_name} response"
                
                elif prop_type == 'number' or prop_type == 'integer':
                    result[prop_name] = random.randint(1, 100)
                
                elif prop_type == 'boolean':
                    result[prop_name] = random.choice([True, False])
                
                elif prop_type == 'array':
                    # Generate a list of 2-4 items
                    result[prop_name] = [f"Item {i}" for i in range(1, random.randint(2, 5))]
                
                elif prop_type == 'object':
                    # Generate a simple nested object
                    result[prop_name] = {"key1": "value1", "key2": "value2"}
        
        return result

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