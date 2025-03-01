#!/usr/bin/env python3
import os
import asyncio
import json
from src.orchestrate.llm import OpenAIClient

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_client_structured_output():
    """
    Test the structured output functionality with our OpenAIClient class.
    """
    print("Testing structured outputs with OpenAIClient...")
    
    # Initialize the OpenAI client
    client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-2024-08-06")
    
    # Define a simple output schema
    output_schema = {
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "The name of a person"
            },
            "age": {
                "type": "integer",
                "description": "The age of the person"
            },
            "hobbies": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "List of hobbies"
            }
        },
        "required": ["name", "age", "hobbies"]
    }
    
    # Test with the structured output format
    try:
        print("\nTesting OpenAIClient.generate_structured method")
        result = await client.generate_structured(
            prompt="Generate information about a fictional person including their name, age, and hobbies.",
            output_schema=output_schema,
            temperature=0.7,
            system_message="You are a helpful assistant."
        )
        
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Check if the result has the expected structure
        if "name" in result and "age" in result and "hobbies" in result:
            print("SUCCESS: Result has the expected structure")
        else:
            print("FAILURE: Result does not have the expected structure")
            if "error" in result:
                print(f"Error: {result['error']}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

async def main():
    await test_client_structured_output()

if __name__ == "__main__":
    asyncio.run(main()) 