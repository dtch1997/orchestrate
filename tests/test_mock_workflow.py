import asyncio
import os
import sys
import time
from pathlib import Path
import pytest

# Set environment variable to use mock LLM
os.environ["ORCHESTRATE_USE_MOCK"] = "true"

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrate.models import Workflow, WorkflowStep
from src.orchestrate.parser import load_workflow_from_file
from src.orchestrate.engine import execute_workflow

@pytest.mark.asyncio
async def test_mock_workflow():
    """Test running a workflow with the mock LLM client."""
    # Find the examples directory
    examples_dir = Path(__file__).parent.parent / "examples"
    
    # Choose a workflow file
    workflow_file = examples_dir / "marketing.yaml"
    
    if not workflow_file.exists():
        print(f"Workflow file not found: {workflow_file}")
        return
    
    print(f"Loading workflow from {workflow_file}")
    workflow = load_workflow_from_file(str(workflow_file))
    
    print(f"Loaded workflow: {workflow.name}")
    print(f"Description: {workflow.description}")
    print(f"Steps: {len(workflow.steps)}")
    print()
    
    # Set up callbacks for progress reporting
    def on_step_start(step_id):
        print(f"Starting step: {step_id}")
        
    def on_step_complete(step_id, result):
        print(f"Completed step: {step_id}")
        print(f"Result: {result}")
        print()
    
    # Execute the workflow
    print(f"Executing workflow: {workflow.name}")
    start_time = time.time()
    
    result = await execute_workflow(
        workflow,
        on_step_start=on_step_start,
        on_step_complete=on_step_complete
    )
    
    # Print summary
    print("\nWorkflow execution complete")
    print(f"Total execution time: {result.total_execution_time:.2f} seconds")
    
    # Print step results
    print("\nStep Results:")
    for step_id, step_result in result.step_results.items():
        print(f"Step: {step_id}")
        print(f"Execution Time: {step_result.execution_time:.2f} seconds")
        print(f"Result: {step_result.result}")
        print()
    
    # Add an assertion to make this a proper test
    assert result is not None
    assert result.total_execution_time > 0
    assert len(result.step_results) > 0

if __name__ == "__main__":
    asyncio.run(test_mock_workflow()) 