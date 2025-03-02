import asyncio
import argparse
import sys
import os
from pathlib import Path
import json

from .models import Workflow, StepIO
from .parser import load_workflow_from_file
from .engine import execute_workflow
from .composer import compose_workflow

def collect_user_inputs(workflow: Workflow) -> dict:
    """
    Collect user inputs required by the workflow.
    
    Args:
        workflow: The workflow to collect inputs for
        
    Returns:
        Dictionary of user inputs
    """
    user_inputs = {}
    required_inputs = set()
    
    # Find all inputs with source="user"
    for step in workflow.steps:
        for input_spec in step.inputs:
            if input_spec.source == "user":
                required_inputs.add(input_spec.name)
    
    if not required_inputs:
        return user_inputs
        
    print("\nThis workflow requires the following inputs:")
    
    # Collect inputs from the user
    for input_name in sorted(required_inputs):
        # Find the input specification to get the description
        description = ""
        for step in workflow.steps:
            for input_spec in step.inputs:
                if input_spec.name == input_name and input_spec.source == "user":
                    description = input_spec.description
                    break
            if description:
                break
                
        prompt = f"{input_name}"
        if description:
            prompt += f" ({description})"
        prompt += ": "
        
        user_input = input(prompt)
        user_inputs[input_name] = user_input
    
    print()  # Add a blank line after inputs
    return user_inputs

async def run_workflow(workflow_path: str, verbose: bool = False, model: str = None, temperature: float = 0.7):
    """
    Run a workflow from a YAML file.
    
    Args:
        workflow_path: Path to the workflow YAML file
        verbose: Whether to print verbose output
        model: The OpenAI model to use
        temperature: The temperature parameter for the model
    """
    try:
        # Load the workflow
        workflow = load_workflow_from_file(workflow_path)
        
        if verbose:
            print(f"Loaded workflow: {workflow.name}")
            print(f"Description: {workflow.description}")
            print(f"Steps: {len(workflow.steps)}")
            print(f"Using model: {model or os.getenv('OPENAI_MODEL', 'gpt-4o')}")
            print(f"Temperature: {temperature}")
            print()
        
        # Collect user inputs
        user_inputs = collect_user_inputs(workflow)
        
        # Set up callbacks for progress reporting
        def on_step_start(step_id):
            print(f"Starting step: {step_id}")
            
        def on_step_complete(step_id, result):
            if verbose:
                print(f"Completed step: {step_id}")
                # Check if result is a string before trying to slice it
                if isinstance(result, str):
                    print(f"Result: {result[:100]}..." if len(result) > 100 else f"Result: {result}")
                elif isinstance(result, dict):
                    # For structured outputs, print a more readable format
                    print(f"Result: {json.dumps(result, indent=2)[:300]}..." if len(json.dumps(result)) > 300 else f"Result: {json.dumps(result, indent=2)}")
                else:
                    print(f"Result: {str(result)[:100]}..." if len(str(result)) > 100 else f"Result: {str(result)}")
                
                # Get the step result from the context
                step_result = None
                for s in workflow.steps:
                    if s.id == step_id:
                        step_result = s
                        break
                
                # Print outputs if available
                if step_result and step_result.outputs:
                    print("\nOutputs:")
                    for output in step_result.outputs:
                        print(f"  {output.name}: {output.description}")
                print()
            else:
                print(f"Completed step: {step_id}")
        
        # Create initial context with model settings and user inputs
        initial_context = {
            "model": model or os.getenv("OPENAI_MODEL", "gpt-4o"),
            "temperature": temperature
        }
        
        # Add user inputs to the context
        initial_context.update(user_inputs)
        
        # Execute the workflow
        print(f"Executing workflow: {workflow.name}")
        result = await execute_workflow(
            workflow,
            initial_context=initial_context,
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
                            "prompt": step_result.prompt,
                            "model": step_result.model,
                            "temperature": step_result.temperature,
                            "system_message": step_result.system_message,
                            "outputs": step_result.outputs,
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
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Run command - execute a workflow
    run_parser = subparsers.add_parser("run", help="Run a workflow")
    run_parser.add_argument("workflow", help="Path to the workflow YAML file")
    run_parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output")
    run_parser.add_argument("--model", help="OpenAI model to use (default: gpt-4o or OPENAI_MODEL env var)")
    run_parser.add_argument("--temperature", type=float, default=0.7, help="Temperature for the model (0.0-1.0)")
    run_parser.add_argument("--use-mock", action="store_true", help="Use mock LLM instead of OpenAI")
    
    # Compose command - generate a workflow
    compose_parser = subparsers.add_parser("compose", help="Generate a workflow using an LLM")
    compose_parser.add_argument("name", help="Name of the workflow")
    compose_parser.add_argument("description", help="Description of what the workflow should do")
    compose_parser.add_argument("-o", "--output", help="Output file to save the generated workflow")
    compose_parser.add_argument("-t", "--temperature", type=float, default=0.7, 
                              help="Temperature for LLM generation (0.0 to 1.0)")
    compose_parser.add_argument("-m", "--model", help="LLM model to use")
    compose_parser.add_argument("--use-mock", action="store_true", help="Use mock LLM instead of OpenAI")
    
    args = parser.parse_args()
    
    # Set mock environment variable if requested
    if hasattr(args, 'use_mock') and args.use_mock:
        os.environ["ORCHESTRATE_USE_MOCK"] = "true"
    
    # Handle default command (for backward compatibility)
    if args.command is None and len(sys.argv) > 1:
        # Assume the first argument is a workflow file path
        workflow_path = sys.argv[1]
        verbose = "-v" in sys.argv or "--verbose" in sys.argv
        
        # Extract model and temperature if provided
        model = None
        temperature = 0.7
        
        for i, arg in enumerate(sys.argv):
            if arg == "--model" and i + 1 < len(sys.argv):
                model = sys.argv[i + 1]
            elif arg == "--temperature" and i + 1 < len(sys.argv):
                try:
                    temperature = float(sys.argv[i + 1])
                except ValueError:
                    pass
        
        # Run the workflow
        asyncio.run(run_workflow(workflow_path, verbose, model, temperature))
        return
    
    # Handle commands
    if args.command == "run":
        # Run the workflow
        asyncio.run(run_workflow(args.workflow, args.verbose, args.model, args.temperature))
    elif args.command == "compose":
        # Generate a workflow
        asyncio.run(compose_workflow(
            name=args.name,
            description=args.description,
            model=args.model,
            temperature=args.temperature,
            output_file=args.output
        ))
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 