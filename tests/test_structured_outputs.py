#!/usr/bin/env python3
import os
import asyncio
import json
from openai import AsyncOpenAI

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_structured_output():
    """
    Test the structured output functionality with OpenAI API.
    """
    print("Testing structured outputs with OpenAI API...")
    
    # Initialize the OpenAI client
    client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
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
    
    # Test with the correct format for json_object
    try:
        print("\nTest 1: Using correct format with response_format.type = 'json_object'")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Generate information about a fictional person including their name, age, and hobbies. Return the result as JSON."}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        print(f"Response: {response.choices[0].message.content}")
        # Try to parse the JSON
        try:
            parsed = json.loads(response.choices[0].message.content)
            print(f"Successfully parsed JSON: {json.dumps(parsed, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
    
    except Exception as e:
        print(f"Error with Test 1: {str(e)}")
    
    # Test with the structured output format using json_schema
    try:
        print("\nTest 2: Using structured outputs with json_schema")
        response = await client.chat.completions.create(
            model="gpt-4o-2024-08-06",  # Make sure to use a model that supports structured outputs
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Generate information about a fictional person including their name, age, and hobbies. Return the result as JSON."}
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "person_info",
                    "schema": output_schema
                }
            },
            temperature=0.7
        )
        
        print(f"Response: {response.choices[0].message.content}")
        # Try to parse the JSON
        try:
            parsed = json.loads(response.choices[0].message.content)
            print(f"Successfully parsed JSON: {json.dumps(parsed, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
    
    except Exception as e:
        print(f"Error with Test 2: {str(e)}")
    
    # Test with the basic json_object format (fallback)
    try:
        print("\nTest 3: Using basic json_object format (fallback)")
        response = await client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Return your response as a JSON object with the following structure: {\"name\": \"person name\", \"age\": person age, \"hobbies\": [\"hobby1\", \"hobby2\", ...]}"},
                {"role": "user", "content": "Generate information about a fictional person including their name, age, and hobbies. Return the result as JSON."}
            ],
            response_format={"type": "json_object"},
            temperature=0.7
        )
        
        print(f"Response: {response.choices[0].message.content}")
        # Try to parse the JSON
        try:
            parsed = json.loads(response.choices[0].message.content)
            print(f"Successfully parsed JSON: {json.dumps(parsed, indent=2)}")
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON: {e}")
    
    except Exception as e:
        print(f"Error with Test 3: {str(e)}")

async def main():
    await test_structured_output()

if __name__ == "__main__":
    asyncio.run(main()) 