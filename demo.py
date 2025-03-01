#!/usr/bin/env python
"""
Demo entry point for Orchestrate with OpenAI integration.

This script loads environment variables from .env and runs the Streamlit app
with the real OpenAI client instead of the mock client.
"""

import os
import sys
from dotenv import load_dotenv
import streamlit.web.cli as stcli

# Ensure the package is in the Python path
sys.path.insert(0, os.path.abspath("."))

def main():
    # Load environment variables from .env file
    load_dotenv()
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY environment variable is not set.")
        print("Please create a .env file in the project root with your OpenAI API key:")
        print("OPENAI_API_KEY=your-api-key-here")
        sys.exit(1)
    
    # Make sure we're NOT using the mock client
    os.environ["ORCHESTRATE_USE_MOCK"] = "false"
    
    # Set default model if not already set
    if not os.getenv("OPENAI_MODEL"):
        os.environ["OPENAI_MODEL"] = "gpt-4o"
    
    print(f"Using OpenAI model: {os.getenv('OPENAI_MODEL')}")
    print("Starting Orchestrate with OpenAI integration...")
    
    # Run the Streamlit app
    sys.argv = ["streamlit", "run", "src/orchestrate/app.py"]
    sys.exit(stcli.main())

if __name__ == "__main__":
    main() 