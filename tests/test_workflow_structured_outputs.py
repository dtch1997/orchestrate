#!/usr/bin/env python3
import os
import asyncio
import json
from src.orchestrate.models import Workflow, WorkflowStep, StepIO
from src.orchestrate.engine import execute_workflow, create_output_schema

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

async def test_workflow_structured_outputs():
    """
    Test that the entire workflow works correctly with structured outputs.
    """
    print("Testing workflow with structured outputs...")
    
    # Create a simple workflow with structured outputs
    workflow = Workflow(
        name="Test Workflow",
        description="A test workflow with structured outputs",
        version="1.0",
        steps=[
            WorkflowStep(
                id="step1",
                prompt="Generate information about a fictional person including their name, age, and hobbies.",
                outputs=[
                    StepIO(name="name", description="The name of a person"),
                    StepIO(name="age", description="The age of the person"),
                    StepIO(name="hobbies", description="List of hobbies")
                ]
            ),
            WorkflowStep(
                id="step2",
                prompt="Generate a short biography for {{name}}, who is {{age}} years old and enjoys {{hobbies}}.",
                inputs=[
                    StepIO(name="name", source="step1", description="The name of a person"),
                    StepIO(name="age", source="step1", description="The age of the person"),
                    StepIO(name="hobbies", source="step1", description="List of hobbies")
                ],
                outputs=[
                    StepIO(name="biography", description="A short biography")
                ]
            )
        ]
    )
    
    # Define callbacks for progress reporting
    def on_step_start(step_id):
        print(f"Starting step: {step_id}")
        
    def on_step_complete(step_id, result):
        print(f"Completed step: {step_id}")
        print(f"Result: {json.dumps(result, indent=2)}")
    
    # Execute the workflow
    try:
        print("\nExecuting workflow...")
        result = await execute_workflow(
            workflow,
            initial_context={
                "model": os.getenv("OPENAI_MODEL", "gpt-4o-2024-08-06"),
                "temperature": 0.7
            },
            on_step_start=on_step_start,
            on_step_complete=on_step_complete
        )
        
        print("\nWorkflow execution complete")
        print(f"Total execution time: {result.total_execution_time:.2f} seconds")
        
        # Check if the workflow executed successfully
        if len(result.step_results) == 2:
            print("SUCCESS: Workflow executed successfully")
            
            # Check if step1 has the expected outputs
            step1_result = result.step_results.get("step1")
            if step1_result and "name" in step1_result.outputs and "age" in step1_result.outputs and "hobbies" in step1_result.outputs:
                print("SUCCESS: Step 1 has the expected outputs")
            else:
                print("FAILURE: Step 1 does not have the expected outputs")
                
            # Check if step2 has the expected outputs
            step2_result = result.step_results.get("step2")
            if step2_result and "biography" in step2_result.outputs:
                print("SUCCESS: Step 2 has the expected outputs")
            else:
                print("FAILURE: Step 2 does not have the expected outputs")
        else:
            print("FAILURE: Workflow did not execute all steps")
    
    except Exception as e:
        print(f"Error: {str(e)}")

async def main():
    await test_workflow_structured_outputs()

if __name__ == "__main__":
    asyncio.run(main()) 