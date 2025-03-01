#!/usr/bin/env python
"""
Demo script for Orchestrate with OpenAI integration.
This script loads environment variables and runs the Streamlit app.
"""

import os
import subprocess
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Check if OPENAI_API_KEY is set
if not os.getenv("OPENAI_API_KEY"):
    print("Warning: OPENAI_API_KEY environment variable is not set.")
    print("The app will run, but OpenAI integration will not work.")
    print("Please set OPENAI_API_KEY in your .env file or environment.")
    print()
    
    # Set to use mock LLM by default if no API key
    os.environ["ORCHESTRATE_USE_MOCK"] = "true"
    print("Using mock LLM client for demonstration purposes.")
else:
    # Make sure ORCHESTRATE_USE_MOCK is not set to true by default
    if os.getenv("ORCHESTRATE_USE_MOCK", "false").lower() != "true":
        os.environ["ORCHESTRATE_USE_MOCK"] = "false"
    
    print("Starting Orchestrate with OpenAI integration...")
    print(f"Using model: {os.getenv('OPENAI_MODEL', 'gpt-4o')}")

print()

# Run the Streamlit app
cmd = ["streamlit", "run", "src/orchestrate/app.py"]

# Execute the command
subprocess.run(cmd) 