# Agent's Guide to Using Orchestrate Composer

This guide explains how LLM agents can leverage Orchestrate's Composer feature to create, execute, and manage AI workflows.

## Overview

Orchestrate's Composer allows agents to generate complete workflow definitions from simple natural language descriptions. This enables agents to:

1. Create custom workflows for specific tasks without manual YAML writing
2. Adapt workflows to changing requirements on the fly
3. Build complex, multi-step processes with proper state management
4. Maintain transparency and explainability in their operations

## Using the Composer as an Agent

### Basic Workflow Generation

As an agent, you can generate a workflow using a simple command:

```bash
python -m src.orchestrate.cli compose "Task Name" "Detailed task description" -o output_file.yaml
```

For example:

```bash
python -m src.orchestrate.cli compose "Customer Feedback Analysis" "Analyze customer feedback, categorize sentiments, identify key themes, and generate actionable insights" -o feedback_analysis.yaml
```

### Programmatic Workflow Generation

For more control, you can use the Python API:

```python
import asyncio
from src.orchestrate.composer import compose_workflow

async def generate_custom_workflow():
    workflow_yaml = await compose_workflow(
        name="Data Processing Pipeline",
        description="Extract data from CSV files, clean and normalize it, perform statistical analysis, and generate visualizations",
        temperature=0.7,
        output_file="data_pipeline.yaml"
    )
    return workflow_yaml

# Run the async function
workflow = asyncio.run(generate_custom_workflow())
```

## Best Practices for Agent-Generated Workflows

### 1. Be Specific in Descriptions

The more specific your description, the better the generated workflow:

**Vague:** "Generate a marketing campaign"

**Specific:** "Create a multi-channel marketing campaign for a new smartphone launch, including target audience analysis, messaging development, content creation for social media, and performance metrics definition"

### 2. Include Input/Output Requirements

Mention the inputs you expect to provide and the outputs you need:

"Generate a workflow that takes a product name and target demographic as inputs, and produces a marketing slogan, three social media post templates, and a list of influencer categories as outputs."

### 3. Specify Step Sequence When Important

If certain steps must happen in a specific order, make that clear:

"The workflow should first analyze the raw data, then classify it into categories, and finally generate a summary report."

### 4. Indicate Integration Points

Mention any systems or data sources the workflow should connect with:

"The workflow should pull data from customer reviews, process it, and prepare it for input into our CRM system."

## Executing Agent-Generated Workflows

Once you've generated a workflow, you can execute it:

```bash
python -m src.orchestrate.cli run generated_workflow.yaml -v
```

Or programmatically:

```python
import asyncio
from src.orchestrate.parser import load_workflow_from_file
from src.orchestrate.engine import execute_workflow

async def run_workflow():
    # Load the workflow
    workflow = load_workflow_from_file("generated_workflow.yaml")
    
    # Execute it
    result = await execute_workflow(workflow)
    
    # Process the results
    for step_id, step_result in result.step_results.items():
        print(f"Step {step_id} result: {step_result.result}")
    
    return result

# Run the async function
result = asyncio.run(run_workflow())
```

## Analyzing and Improving Workflows

After execution, you can analyze the results to improve the workflow:

1. Examine the execution time of each step
2. Review the prompts and responses for each step
3. Identify any steps that could be optimized or refined
4. Generate an improved workflow based on your analysis

## Example: Agent-Driven Workflow Improvement Loop

```python
import asyncio
from src.orchestrate.composer import compose_workflow
from src.orchestrate.parser import load_workflow_from_yaml
from src.orchestrate.engine import execute_workflow

async def improve_workflow(original_yaml, execution_result):
    # Analyze the execution result
    total_time = execution_result.total_execution_time
    step_times = {step_id: result.execution_time for step_id, result in execution_result.step_results.items()}
    slowest_step = max(step_times, key=step_times.get)
    
    # Generate improvement suggestions
    improvement_description = f"""
    Create an improved version of a workflow with the following characteristics:
    - Original workflow took {total_time:.2f} seconds to execute
    - The slowest step was '{slowest_step}' at {step_times[slowest_step]:.2f} seconds
    - The workflow should maintain the same overall purpose but optimize for efficiency
    - Consider breaking down complex steps into smaller ones
    - Ensure proper data flow between steps
    
    Original workflow purpose: [extract from original YAML]
    """
    
    # Generate improved workflow
    improved_yaml = await compose_workflow(
        name="Improved Workflow",
        description=improvement_description,
        temperature=0.7
    )
    
    return improved_yaml

# Usage example
async def workflow_improvement_loop():
    # Initial workflow
    workflow_yaml = await compose_workflow(
        name="Initial Workflow",
        description="Process customer feedback and generate insights",
        temperature=0.7
    )
    
    # Execute it
    workflow = load_workflow_from_yaml(workflow_yaml)
    result = await execute_workflow(workflow)
    
    # Improve it
    improved_yaml = await improve_workflow(workflow_yaml, result)
    
    # Execute improved workflow
    improved_workflow = load_workflow_from_yaml(improved_yaml)
    improved_result = await execute_workflow(improved_workflow)
    
    # Compare results
    print(f"Original execution time: {result.total_execution_time:.2f}s")
    print(f"Improved execution time: {improved_result.total_execution_time:.2f}s")
```

## Conclusion

The Composer feature enables agents to be more autonomous and effective by allowing them to create custom workflows on demand. By following the best practices in this guide, agents can generate high-quality workflows that accomplish complex tasks while maintaining transparency and control. 