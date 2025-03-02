"""
Workflow Compiler for Orchestrate.

This module provides functionality to validate workflow YAML files and generate
a workflow specification that summarizes the inputs and outputs.
"""

import sys
from typing import Dict, List, Set, Tuple, Any, Optional
from pathlib import Path

from .models import Workflow, WorkflowStep, StepIO
from .parser import load_workflow_from_file, load_workflow_from_yaml

class ValidationError(Exception):
    """Exception raised for workflow validation errors."""
    pass

class WorkflowSpec:
    """
    Specification of a validated workflow.
    
    Attributes:
        name: Name of the workflow
        description: Description of the workflow
        user_inputs: List of inputs required from the user
        final_outputs: List of outputs produced by the workflow
        is_valid: Whether the workflow is valid
        validation_errors: List of validation errors if any
    """
    
    def __init__(self, 
                name: str, 
                description: str, 
                user_inputs: List[StepIO], 
                final_outputs: List[StepIO],
                is_valid: bool = True,
                validation_errors: List[str] = None):
        self.name = name
        self.description = description
        self.user_inputs = user_inputs
        self.final_outputs = final_outputs
        self.is_valid = is_valid
        self.validation_errors = validation_errors or []
    
    def __str__(self) -> str:
        """String representation of the workflow specification."""
        result = [
            f"Workflow: {self.name}",
            f"Description: {self.description}",
            f"Valid: {'Yes' if self.is_valid else 'No'}"
        ]
        
        if not self.is_valid:
            result.append("\nValidation Errors:")
            for error in self.validation_errors:
                result.append(f"- {error}")
        
        result.append("\nUser Inputs:")
        if self.user_inputs:
            for input_spec in self.user_inputs:
                desc = f" ({input_spec.description})" if input_spec.description else ""
                result.append(f"- {input_spec.name}{desc}")
        else:
            result.append("- None")
        
        result.append("\nWorkflow Outputs:")
        if self.final_outputs:
            for output_spec in self.final_outputs:
                desc = f" ({output_spec.description})" if output_spec.description else ""
                result.append(f"- {output_spec.name}{desc}")
        else:
            result.append("- None")
        
        return "\n".join(result)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow specification to a dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "is_valid": self.is_valid,
            "validation_errors": self.validation_errors,
            "user_inputs": [
                {"name": inp.name, "description": inp.description}
                for inp in self.user_inputs
            ],
            "final_outputs": [
                {"name": out.name, "description": out.description}
                for out in self.final_outputs
            ]
        }

def compile_workflow(workflow: Workflow) -> WorkflowSpec:
    """
    Compile a workflow to validate it and generate a specification.
    
    Args:
        workflow: The workflow to compile
        
    Returns:
        A WorkflowSpec object containing the workflow specification
        
    Raises:
        ValidationError: If the workflow is invalid
    """
    validation_errors = []
    
    # Track available outputs and used inputs
    available_outputs: Dict[str, Dict[str, StepIO]] = {}  # step_id -> {output_name: StepIO}
    user_inputs: List[StepIO] = []
    final_outputs: List[StepIO] = []
    
    # First pass: collect all outputs from each step
    for step in workflow.steps:
        available_outputs[step.id] = {}
        for output in step.outputs:
            available_outputs[step.id][output.name] = output
    
    # Second pass: validate inputs and collect user inputs
    for step_index, step in enumerate(workflow.steps):
        # Check if all inputs are either from user or from previous steps
        for input_spec in step.inputs:
            if input_spec.source == "user":
                # Add to user inputs if not already there
                if not any(ui.name == input_spec.name for ui in user_inputs):
                    user_inputs.append(input_spec)
            elif input_spec.source:
                # Check if the source step exists
                if input_spec.source not in available_outputs:
                    validation_errors.append(
                        f"Step '{step.id}' references non-existent source step '{input_spec.source}' for input '{input_spec.name}'"
                    )
                    continue
                
                # Check if the source step is before this step
                source_step_index = next(
                    (i for i, s in enumerate(workflow.steps) if s.id == input_spec.source), 
                    None
                )
                if source_step_index is None or source_step_index >= step_index:
                    validation_errors.append(
                        f"Step '{step.id}' references source step '{input_spec.source}' that is not defined before it"
                    )
                    continue
                
                # Check if the output exists in the source step
                if input_spec.name not in available_outputs[input_spec.source]:
                    validation_errors.append(
                        f"Step '{step.id}' references non-existent output '{input_spec.name}' from step '{input_spec.source}'"
                    )
            else:
                validation_errors.append(
                    f"Step '{step.id}' has input '{input_spec.name}' with no source specified"
                )
        
        # Check if all inputs are used in the prompt
        for input_spec in step.inputs:
            input_var = f"{{{{{input_spec.name}}}}}"
            if input_var not in step.prompt:
                validation_errors.append(
                    f"Step '{step.id}' has input '{input_spec.name}' that is not used in the prompt"
                )
    
    # Collect final outputs (outputs from the last step)
    if workflow.steps:
        last_step = workflow.steps[-1]
        final_outputs = last_step.outputs
    
    # Create the workflow specification
    is_valid = len(validation_errors) == 0
    spec = WorkflowSpec(
        name=workflow.name,
        description=workflow.description,
        user_inputs=user_inputs,
        final_outputs=final_outputs,
        is_valid=is_valid,
        validation_errors=validation_errors
    )
    
    return spec

def compile_from_file(file_path: str) -> WorkflowSpec:
    """
    Compile a workflow from a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        A WorkflowSpec object containing the workflow specification
    """
    workflow = load_workflow_from_file(file_path)
    return compile_workflow(workflow)

def compile_from_yaml(yaml_content: str) -> WorkflowSpec:
    """
    Compile a workflow from YAML content.
    
    Args:
        yaml_content: YAML content as a string
        
    Returns:
        A WorkflowSpec object containing the workflow specification
    """
    workflow = load_workflow_from_yaml(yaml_content)
    return compile_workflow(workflow)

def main():
    """Command line interface for the compiler."""
    if len(sys.argv) < 2:
        print("Usage: python -m orchestrate.compiler <workflow.yaml>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    try:
        spec = compile_from_file(file_path)
        print(spec)
        
        if not spec.is_valid:
            sys.exit(1)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 