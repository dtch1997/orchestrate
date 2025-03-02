"""
Composer module for Orchestrate.

This module provides functionality to automatically generate workflows using an LLM
based on a name and description provided by the user.
"""

import os
import argparse
import asyncio
from typing import Optional, Dict, Any

from .llm import generate_completion
from .parser import load_workflow_from_yaml
from .models import Workflow

async def compose_workflow(
    name: str,
    description: str,
    model: Optional[str] = None,
    temperature: float = 0.7,
    output_file: Optional[str] = None
) -> str:
    """
    Generate a workflow YAML using an LLM based on a name and description.
    
    Args:
        name: The name of the workflow
        description: A description of what the workflow should do
        model: The LLM model to use (defaults to environment variable or gpt-4o)
        temperature: The temperature to use for generation (0.0 to 1.0)
        output_file: Optional path to save the generated workflow
        
    Returns:
        The generated workflow YAML as a string
    """
    # Construct the prompt for the LLM
    prompt = f"""
You are an expert workflow designer for an AI orchestration system. Your task is to create a YAML workflow definition based on the name and description provided.

Workflow Name: {name}
Workflow Description: {description}

The workflow should be defined in YAML format with the following structure:

```yaml
name: [Workflow Name]
description: [Workflow Description]
version: "1.0"

steps:
  - id: [step_id]
    prompt: >
      [The prompt that will be sent to the LLM for this step]
    inputs:
      - name: [input_name]
        source: [source_step_id or "user"]
        description: [Description of the input]
    outputs:
      - name: [output_name]
        description: [Description of the output]

  # Additional steps...
```

Guidelines:
1. Create a logical sequence of steps that accomplishes the workflow goal
2. Each step should have a clear purpose and well-defined inputs/outputs
3. The first step should typically get input from the user (source: "user")
4. Subsequent steps should reference outputs from previous steps
5. Make prompts clear and specific, including placeholders like {{variable_name}} for inputs
6. Ensure the workflow is coherent and each step builds on previous steps
7. Include 3-7 steps depending on the complexity of the task
8. Use descriptive step IDs and output names

Please generate a complete, valid YAML workflow definition following these guidelines.
"""

    # Generate the workflow YAML using the LLM
    system_message = "You are an expert workflow designer for an AI orchestration system. Create valid YAML workflows that follow the specified format exactly."
    
    yaml_content = await generate_completion(
        prompt=prompt,
        temperature=temperature,
        system_message=system_message
    )
    
    # Extract the YAML content if it's wrapped in markdown code blocks
    if "```yaml" in yaml_content and "```" in yaml_content.split("```yaml", 1)[1]:
        yaml_content = yaml_content.split("```yaml", 1)[1].split("```", 1)[0].strip()
    elif "```" in yaml_content and "```" in yaml_content.split("```", 1)[1]:
        yaml_content = yaml_content.split("```", 1)[1].split("```", 1)[0].strip()
    
    # Validate the generated YAML
    try:
        workflow = load_workflow_from_yaml(yaml_content)
        print(f"Successfully generated workflow '{workflow.name}' with {len(workflow.steps)} steps")
    except Exception as e:
        print(f"Warning: Generated workflow may not be valid: {str(e)}")
    
    # Save to file if requested
    if output_file:
        with open(output_file, "w") as f:
            f.write(yaml_content)
        print(f"Workflow saved to {output_file}")
    
    return yaml_content

def main():
    """Command line interface for the composer."""
    parser = argparse.ArgumentParser(description="Generate workflows using an LLM")
    parser.add_argument("name", help="Name of the workflow")
    parser.add_argument("description", help="Description of what the workflow should do")
    parser.add_argument("--output", "-o", help="Output file to save the generated workflow")
    parser.add_argument("--temperature", "-t", type=float, default=0.7, 
                        help="Temperature for LLM generation (0.0 to 1.0)")
    parser.add_argument("--model", "-m", help="LLM model to use")
    
    args = parser.parse_args()
    
    # Run the async function
    asyncio.run(compose_workflow(
        name=args.name,
        description=args.description,
        model=args.model,
        temperature=args.temperature,
        output_file=args.output
    ))

if __name__ == "__main__":
    main() 