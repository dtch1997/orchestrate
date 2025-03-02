#!/usr/bin/env python
"""
Example script demonstrating how to use the Compiler programmatically.

This script shows how to validate a workflow and generate a specification.
"""

import sys
import json
from pathlib import Path

from orchestrate.compiler import compile_from_file, compile_from_yaml
from orchestrate.composer import compose_workflow
import asyncio

async def main():
    """Demonstrate the compiler functionality."""
    print("=== Orchestrate Compiler Example ===")
    
    # Example 1: Compile an existing workflow
    workflow_path = "examples/debate.yaml"
    print(f"\nCompiling existing workflow: {workflow_path}")
    
    try:
        # Compile the workflow
        spec = compile_from_file(workflow_path)
        
        # Print the specification
        print("\nWorkflow Specification:")
        print(spec)
        
        # Print in JSON format
        print("\nJSON Specification:")
        print(json.dumps(spec.to_dict(), indent=2))
        
        # Check if the workflow is valid
        if spec.is_valid:
            print("\n✅ Workflow is valid!")
        else:
            print("\n❌ Workflow has validation errors:")
            for error in spec.validation_errors:
                print(f"  - {error}")
    except Exception as e:
        print(f"Error compiling workflow: {str(e)}")
    
    # Example 2: Generate a workflow with Composer and validate it with Compiler
    print("\n=== Generate and Validate a Workflow ===")
    
    try:
        # Generate a workflow
        name = "Customer Feedback Analysis"
        description = "Analyze customer feedback, categorize sentiments, identify key themes, and generate actionable insights"
        
        print(f"\nGenerating workflow: {name}")
        yaml_content = await compose_workflow(
            name=name,
            description=description,
            temperature=0.7
        )
        
        # Compile the generated workflow
        print("\nValidating the generated workflow...")
        spec = compile_from_yaml(yaml_content)
        
        # Print the specification
        print("\nWorkflow Specification:")
        print(spec)
        
        # Check if the workflow is valid
        if spec.is_valid:
            print("\n✅ Generated workflow is valid!")
            
            # Save the workflow to a file
            output_file = "examples/generated_feedback_workflow.yaml"
            with open(output_file, "w") as f:
                f.write(yaml_content)
            print(f"\nWorkflow saved to {output_file}")
        else:
            print("\n❌ Generated workflow has validation errors:")
            for error in spec.validation_errors:
                print(f"  - {error}")
    except Exception as e:
        print(f"Error generating and validating workflow: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 