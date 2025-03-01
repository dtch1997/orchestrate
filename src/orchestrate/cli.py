import asyncio
import argparse
import sys
import os
from pathlib import Path
import json

from .models import Workflow
from .parser import load_workflow_from_file
from .engine import execute_workflow

async def run_workflow(workflow_path: str, verbose: bool = False):
    """
    Run a workflow from a YAML file.
    
    Args:
        workflow_path: Path to the workflow YAML file
        verbose: Whether to print verbose output
    """
    try:
        # Load the workflow
        workflow = load_workflow_from_file(workflow_path)
        
        if verbose:
            print(f"Loaded workflow: {workflow.name}")
            print(f"Description: {workflow.description}")
            print(f"Steps: {len(workflow.steps)}")
            print()
        
        # Set up callbacks for progress reporting
        def on_step_start(step_id):
            print(f"Starting step: {step_id}")
            
        def on_step_complete(step_id, result):
            if verbose:
                print(f"Completed step: {step_id}")
                print(f"Result: {result[:100]}..." if len(str(result)) > 100 else f"Result: {result}")
                print()
            else:
                print(f"Completed step: {step_id}")
        
        # Execute the workflow
        print(f"Executing workflow: {workflow.name}")
        result = await execute_workflow(
            workflow,
            on_step_start=on_step_start,
            on_step_complete=on_step_complete
        )
        
        # Print summary
        print("\nWorkflow execution complete")
        print(f"Total execution time: {result.total_execution_time:.2f} seconds")
        
        # Save results to file if requested
        if verbose:
            output_path = Path(workflow_path).with_suffix('.result.json')
            with open(output_path, 'w') as f:
                # Convert to dict for JSON serialization
                result_dict = {
                    "workflow_name": result.workflow_name,
                    "total_execution_time": result.total_execution_time,
                    "step_results": {
                        step_id: {
                            "step_id": step_result.step_id,
                            "result": step_result.result,
                            "execution_time": step_result.execution_time
                        }
                        for step_id, step_result in result.step_results.items()
                    }
                }
                json.dump(result_dict, f, indent=2)
            print(f"Results saved to {output_path}")
            
        return result
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return None

def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Orchestrate - Workflow Orchestration Tool")
    parser.add_argument("workflow", help="Path to the workflow YAML file")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    
    args = parser.parse_args()
    
    # Run the workflow
    asyncio.run(run_workflow(args.workflow, args.verbose))

if __name__ == "__main__":
    main() 