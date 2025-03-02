#!/usr/bin/env python
"""
Example script demonstrating how to use the Composer programmatically.

This script shows how to generate a workflow using the Composer and then
execute it immediately.
"""

import asyncio
import os
from pathlib import Path

from src.orchestrate.composer import compose_workflow
from src.orchestrate.parser import load_workflow_from_yaml
from src.orchestrate.engine import execute_workflow

async def main():
    """Generate and run a workflow."""
    print("=== Orchestrate Composer Example ===")
    
    # Define the workflow parameters
    name = "Recipe Generator"
    description = "Generate a recipe based on available ingredients and dietary preferences"
    
    print(f"\nGenerating workflow: {name}")
    print(f"Description: {description}")
    
    # Generate the workflow
    yaml_content = await compose_workflow(
        name=name,
        description=description,
        temperature=0.7
    )
    
    # Save the workflow to a file
    output_file = "examples/generated_recipe_workflow.yaml"
    with open(output_file, "w") as f:
        f.write(yaml_content)
    print(f"\nWorkflow saved to {output_file}")
    
    # Load the workflow
    workflow = load_workflow_from_yaml(yaml_content)
    
    # Ask if the user wants to run the workflow
    response = input("\nDo you want to run this workflow now? (y/n): ")
    if response.lower() != "y":
        print("Exiting without running the workflow.")
        return
    
    print("\n=== Running Workflow ===")
    
    # Execute the workflow
    result = await execute_workflow(
        workflow=workflow,
        on_step_start=lambda step_id: print(f"Starting step: {step_id}"),
        on_step_complete=lambda step_id, result: print(f"Completed step: {step_id}")
    )
    
    # Print the results
    print("\n=== Workflow Results ===")
    for step_id, step_result in result.step_results.items():
        print(f"\n--- {step_id} ---")
        print(step_result.result)
    
    print(f"\nTotal execution time: {result.total_execution_time:.2f} seconds")

if __name__ == "__main__":
    # Set mock LLM if needed for testing
    # os.environ["ORCHESTRATE_USE_MOCK"] = "true"
    
    asyncio.run(main()) 