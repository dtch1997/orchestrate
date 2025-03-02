#!/usr/bin/env python
"""
Command-line interface for the Orchestrate Workflow Compiler.

This script provides a simple way to validate workflows and generate
workflow specifications from the command line.

Example usage:
    python -m orchestrate.cli_compile examples/debate.yaml
    python -m orchestrate.cli_compile examples/debate.yaml --json
"""

import sys
import json
import argparse
from pathlib import Path

from .compiler import compile_from_file, compile_from_yaml, WorkflowSpec

def main():
    """Entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Orchestrate Workflow Compiler")
    parser.add_argument("workflow", help="Path to the workflow YAML file")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--output", "-o", help="Output file to save the specification")
    
    args = parser.parse_args()
    
    try:
        # Compile the workflow
        spec = compile_from_file(args.workflow)
        
        # Prepare the output
        if args.json:
            output = json.dumps(spec.to_dict(), indent=2)
        else:
            output = str(spec)
        
        # Output to file or stdout
        if args.output:
            with open(args.output, "w") as f:
                f.write(output)
            print(f"Workflow specification saved to {args.output}")
        else:
            print(output)
        
        # Exit with error code if workflow is invalid
        if not spec.is_valid:
            sys.exit(1)
            
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main() 