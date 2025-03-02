import json
import sys
import os
from typing import Dict, Any, Optional, List
import argparse
from pathlib import Path
import textwrap
from datetime import datetime

from .models import WorkflowResult, StepResult, Workflow, WorkflowStep
from .parser import load_workflow_from_file

# ANSI color codes for terminal output
COLORS = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "CYAN": "\033[96m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
    "BOLD": "\033[1m",
    "UNDERLINE": "\033[4m"
}

def format_time(seconds: float) -> str:
    """Format time in seconds to a human-readable string."""
    if seconds < 1:
        return f"{seconds * 1000:.2f}ms"
    elif seconds < 60:
        return f"{seconds:.2f}s"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.2f}s"

def format_json(data: Dict[str, Any], indent: int = 2) -> str:
    """Format JSON data with proper indentation and colors."""
    return json.dumps(data, indent=indent)

def truncate_text(text: str, max_length: int = 100, add_ellipsis: bool = True) -> str:
    """Truncate text to a maximum length."""
    if len(text) <= max_length:
        return text
    return text[:max_length] + ("..." if add_ellipsis else "")

def wrap_text(text: str, width: int = 80, initial_indent: str = "", subsequent_indent: str = "") -> str:
    """Wrap text to a specified width."""
    return textwrap.fill(
        text, 
        width=width, 
        initial_indent=initial_indent, 
        subsequent_indent=subsequent_indent
    )

def format_result(result: Any, max_length: int = 1000) -> str:
    """Format a result based on its type."""
    if isinstance(result, dict):
        # Format as JSON
        formatted = format_json(result)
        if len(formatted) > max_length:
            formatted = formatted[:max_length] + "..."
        return formatted
    elif isinstance(result, str):
        # Format as text
        if len(result) > max_length:
            return truncate_text(result, max_length)
        return result
    else:
        # Convert to string and format
        return truncate_text(str(result), max_length)

def print_step_result(step_id: str, step_result: StepResult, verbose: bool = False, 
                      show_prompt: bool = False, show_full_result: bool = False, 
                      show_full_outputs: bool = False, width: int = 80) -> None:
    """Print a formatted step result to the console."""
    print(f"{COLORS['BOLD']}{COLORS['BLUE']}Step: {step_id}{COLORS['ENDC']}")
    print(f"{COLORS['CYAN']}Execution Time: {format_time(step_result.execution_time)}{COLORS['ENDC']}")
    
    if show_prompt and step_result.prompt:
        print(f"\n{COLORS['YELLOW']}Prompt:{COLORS['ENDC']}")
        print(wrap_text(step_result.prompt, width=width, initial_indent="  ", subsequent_indent="  "))
    
    if show_full_result:
        print(f"\n{COLORS['GREEN']}Result:{COLORS['ENDC']}")
        formatted_result = format_result(step_result.result)
        print(wrap_text(formatted_result, width=width, initial_indent="  ", subsequent_indent="  "))
    
    if step_result.outputs and len(step_result.outputs) > 0:
        print(f"\n{COLORS['YELLOW']}Outputs:{COLORS['ENDC']}")
        for name, value in step_result.outputs.items():
            if show_full_outputs:
                # Format and wrap the full output
                formatted_value = str(value)
                print(f"  {COLORS['BOLD']}{name}:{COLORS['ENDC']}")
                print(wrap_text(formatted_value, width=width, initial_indent="    ", subsequent_indent="    "))
            else:
                # Truncate the output as before
                print(f"  {COLORS['BOLD']}{name}:{COLORS['ENDC']} {truncate_text(str(value), 100)}")
    
    if verbose:
        if step_result.model:
            print(f"\n{COLORS['CYAN']}Model: {step_result.model}{COLORS['ENDC']}")
        if step_result.temperature is not None:
            print(f"{COLORS['CYAN']}Temperature: {step_result.temperature}{COLORS['ENDC']}")
    
    print("\n" + "-" * width)

def visualize_workflow_result(result: WorkflowResult, workflow: Optional[Workflow] = None,
                             verbose: bool = False, show_prompts: bool = False,
                             show_full_results: bool = False, show_full_outputs: bool = False,
                             width: int = 80) -> None:
    """
    Visualize a workflow result in the terminal.
    
    Args:
        result: The workflow result to visualize
        workflow: Optional workflow definition for additional context
        verbose: Whether to show verbose output
        show_prompts: Whether to show the prompts used for each step
        show_full_results: Whether to show the full result of each step
        show_full_outputs: Whether to show the full outputs without truncation
        width: Width of the terminal output
    """
    print("\n" + "=" * width)
    print(f"{COLORS['BOLD']}{COLORS['HEADER']}Workflow: {result.workflow_name}{COLORS['ENDC']}")
    print(f"{COLORS['CYAN']}Total Execution Time: {format_time(result.total_execution_time)}{COLORS['ENDC']}")
    print(f"{COLORS['CYAN']}Steps: {len(result.step_results)}{COLORS['ENDC']}")
    print("=" * width + "\n")
    
    # If we have the workflow definition, use it to get the step order
    step_ids = list(result.step_results.keys())
    if workflow:
        step_ids = [step.id for step in workflow.steps]
    
    # Print each step result in order
    for step_id in step_ids:
        if step_id in result.step_results:
            print_step_result(
                step_id, 
                result.step_results[step_id], 
                verbose=verbose,
                show_prompt=show_prompts,
                show_full_result=show_full_results,
                show_full_outputs=show_full_outputs,
                width=width
            )

def load_result_from_file(file_path: str) -> WorkflowResult:
    """
    Load a workflow result from a JSON file.
    
    Args:
        file_path: Path to the result JSON file
        
    Returns:
        The loaded workflow result
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Convert the loaded data to a WorkflowResult
    step_results = {}
    for step_id, step_data in data.get("step_results", {}).items():
        step_results[step_id] = StepResult(
            step_id=step_data.get("step_id", step_id),
            result=step_data.get("result", ""),
            outputs=step_data.get("outputs", {}),
            execution_time=step_data.get("execution_time", 0.0),
            prompt=step_data.get("prompt"),
            model=step_data.get("model"),
            temperature=step_data.get("temperature"),
            system_message=step_data.get("system_message")
        )
    
    return WorkflowResult(
        workflow_name=data.get("workflow_name", "Unknown"),
        step_results=step_results,
        total_execution_time=data.get("total_execution_time", 0.0)
    )

def find_workflow_file(result_file_path: str) -> Optional[str]:
    """
    Try to find the corresponding workflow file for a result file.
    
    Args:
        result_file_path: Path to the result file
        
    Returns:
        Path to the workflow file if found, None otherwise
    """
    # Remove the .result.json suffix and try with .yaml or .yml
    base_path = result_file_path.replace('.result.json', '')
    for ext in ['.yaml', '.yml']:
        workflow_path = base_path + ext
        if os.path.exists(workflow_path):
            return workflow_path
    return None

def main():
    """Main entry point for the visualizer CLI."""
    parser = argparse.ArgumentParser(description="Orchestrate - Workflow Result Visualizer")
    parser.add_argument("result_file", help="Path to the workflow result JSON file")
    parser.add_argument("-w", "--workflow", help="Path to the workflow YAML file (optional)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Show verbose output")
    parser.add_argument("-p", "--show-prompts", action="store_true", help="Show prompts used for each step")
    parser.add_argument("-r", "--show-results", action="store_true", help="Show full results of each step")
    parser.add_argument("-f", "--show-full-outputs", action="store_true", help="Show full outputs without truncation")
    parser.add_argument("--width", type=int, default=80, help="Width of the terminal output")
    
    args = parser.parse_args()
    
    try:
        # Load the result file
        result = load_result_from_file(args.result_file)
        
        # Try to find the workflow file if not specified
        workflow = None
        workflow_path = args.workflow
        if not workflow_path:
            workflow_path = find_workflow_file(args.result_file)
        
        # Load the workflow if available
        if workflow_path and os.path.exists(workflow_path):
            try:
                workflow = load_workflow_from_file(workflow_path)
            except Exception as e:
                print(f"Warning: Could not load workflow file: {str(e)}", file=sys.stderr)
        
        # Visualize the result
        visualize_workflow_result(
            result,
            workflow=workflow,
            verbose=args.verbose,
            show_prompts=args.show_prompts,
            show_full_results=args.show_results,
            show_full_outputs=args.show_full_outputs,
            width=args.width
        )
        
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 