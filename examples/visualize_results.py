#!/usr/bin/env python3
"""
Example script demonstrating how to use the workflow result visualizer programmatically.
"""

import sys
import os
import argparse
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrate import load_workflow_from_file, load_result_from_file, visualize_workflow_result

def main():
    """Main entry point for the example script."""
    parser = argparse.ArgumentParser(description="Example: Visualize Workflow Results")
    parser.add_argument("result_file", help="Path to the workflow result JSON file")
    parser.add_argument("-w", "--workflow", help="Path to the workflow YAML file (optional)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("-p", "--show-prompts", action="store_true", help="Show prompts used for each step")
    
    args = parser.parse_args()
    
    try:
        # Load the result file
        print(f"Loading result file: {args.result_file}")
        result = load_result_from_file(args.result_file)
        
        # Load the workflow file if specified
        workflow = None
        if args.workflow:
            print(f"Loading workflow file: {args.workflow}")
            workflow = load_workflow_from_file(args.workflow)
        
        # Visualize the result
        print("Visualizing workflow result...")
        visualize_workflow_result(
            result,
            workflow=workflow,
            verbose=args.verbose,
            show_prompts=args.show_prompts
        )
        
        return 0
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 