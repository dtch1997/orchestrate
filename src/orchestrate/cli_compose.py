#!/usr/bin/env python
"""
Command-line interface for the Orchestrate Composer.

This script provides a simple way to generate workflows using the Composer
from the command line.

Example usage:
    python -m orchestrate.cli_compose "Marketing Campaign" "Generate a marketing campaign for a new product launch" -o marketing.yaml
"""

import asyncio
import sys
from .composer import compose_workflow

async def main_async():
    """Run the composer with command line arguments."""
    if len(sys.argv) < 3:
        print("Usage: python -m orchestrate.cli_compose <name> <description> [--output <file>] [--temperature <temp>]")
        print("Example: python -m orchestrate.cli_compose \"Marketing Campaign\" \"Generate a marketing campaign\" -o marketing.yaml")
        sys.exit(1)
    
    name = sys.argv[1]
    description = sys.argv[2]
    
    # Parse optional arguments
    output_file = None
    temperature = 0.7
    model = None
    
    i = 3
    while i < len(sys.argv):
        if sys.argv[i] in ["-o", "--output"] and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] in ["-t", "--temperature"] and i + 1 < len(sys.argv):
            try:
                temperature = float(sys.argv[i + 1])
                if temperature < 0 or temperature > 1:
                    print("Temperature must be between 0.0 and 1.0")
                    sys.exit(1)
            except ValueError:
                print("Temperature must be a number between 0.0 and 1.0")
                sys.exit(1)
            i += 2
        elif sys.argv[i] in ["-m", "--model"] and i + 1 < len(sys.argv):
            model = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            sys.exit(1)
    
    # Generate the workflow
    yaml_content = await compose_workflow(
        name=name,
        description=description,
        model=model,
        temperature=temperature,
        output_file=output_file
    )
    
    # If no output file was specified, print to stdout
    if not output_file:
        print("\nGenerated Workflow YAML:")
        print("------------------------")
        print(yaml_content)

def main():
    """Entry point for the CLI."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main() 