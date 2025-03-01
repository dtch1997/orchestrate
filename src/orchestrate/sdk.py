"""
Orchestrate SDK - Fluid interface for building workflows programmatically.

This module provides a fluent API for creating, modifying, and executing workflows
in code, as an alternative to the YAML-based approach.
"""

from typing import List, Dict, Any, Optional, Union, TypeVar, Generic, Callable, Type, cast, overload
from contextlib import contextmanager
import yaml
from pathlib import Path
import textwrap

from .models import Workflow as WorkflowModel
from .models import WorkflowStep as WorkflowStepModel
from .models import StepIO as StepIOModel
from .parser import workflow_to_yaml, load_workflow_from_yaml, load_workflow_from_file

# Type variables for generic typing
T = TypeVar('T')
OutputT = TypeVar('OutputT')


class Input:
    """Builder class for step inputs."""
    
    def __init__(self, name: str, source: Optional[str] = None, description: str = ""):
        """
        Initialize an input specification.
        
        Args:
            name: Name of the input
            source: Source of the input (step_id or 'user')
            description: Optional description
        """
        self.name = name
        self.source = source
        self.description = description
    
    def to_model(self) -> StepIOModel:
        """Convert to StepIO model."""
        return StepIOModel(
            name=self.name,
            source=self.source,
            description=self.description
        )


class Output:
    """Builder class for step outputs."""
    
    def __init__(self, name: str, description: str = ""):
        """
        Initialize an output specification.
        
        Args:
            name: Name of the output
            description: Optional description
        """
        self.name = name
        self.description = description
    
    def to_model(self) -> StepIOModel:
        """Convert to StepIO model."""
        return StepIOModel(
            name=self.name,
            description=self.description
        )


class Step:
    """Builder class for workflow steps with a fluent interface."""
    
    def __init__(self, id: str):
        """
        Initialize a step builder.
        
        Args:
            id: Unique identifier for the step
        """
        self.id = id
        self._prompt = ""
        self._inputs: List[Input] = []
        self._outputs: List[Output] = []
        self._parent_workflow: Optional['Workflow'] = None
    
    def prompt(self, text: str) -> 'Step':
        """
        Set the prompt text for this step.
        
        Args:
            text: The prompt text
            
        Returns:
            Self for method chaining
        """
        # Clean up the prompt text by removing extra whitespace and newlines
        self._prompt = textwrap.dedent(text).strip()
        return self
    
    def add_input(self, name: str, source: Optional[str] = None, description: str = "") -> 'Step':
        """
        Add an input to this step.
        
        Args:
            name: Name of the input
            source: Source of the input (step_id or 'user')
            description: Optional description
            
        Returns:
            Self for method chaining
        """
        self._inputs.append(Input(name=name, source=source, description=description))
        return self
    
    def add_output(self, name: str, description: str = "") -> 'Step':
        """
        Add an output to this step.
        
        Args:
            name: Name of the output
            description: Optional description
            
        Returns:
            Self for method chaining
        """
        self._outputs.append(Output(name=name, description=description))
        return self
    
    def to_model(self) -> WorkflowStepModel:
        """Convert to WorkflowStep model."""
        return WorkflowStepModel(
            id=self.id,
            prompt=self._prompt,
            inputs=[input.to_model() for input in self._inputs],
            outputs=[output.to_model() for output in self._outputs]
        )
    
    def __enter__(self) -> 'Step':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - add step to parent workflow if available."""
        if self._parent_workflow is not None:
            self._parent_workflow.add_step(self)


class Workflow:
    """Builder class for workflows with a fluent interface."""
    
    def __init__(self, name: str):
        """
        Initialize a workflow builder.
        
        Args:
            name: Name of the workflow
        """
        self.name = name
        self._description = ""
        self._version = ""
        self._steps: List[Step] = []
    
    def description(self, text: str) -> 'Workflow':
        """
        Set the description for this workflow.
        
        Args:
            text: The description text
            
        Returns:
            Self for method chaining
        """
        self._description = text
        return self
    
    def version(self, version: str) -> 'Workflow':
        """
        Set the version for this workflow.
        
        Args:
            version: The version string
            
        Returns:
            Self for method chaining
        """
        self._version = version
        return self
    
    def add_step(self, step: Step) -> 'Workflow':
        """
        Add a step to this workflow.
        
        Args:
            step: The step to add
            
        Returns:
            Self for method chaining
        """
        self._steps.append(step)
        return self
    
    def add_steps(self, steps: List[Step]) -> 'Workflow':
        """
        Add multiple steps to this workflow.
        
        Args:
            steps: List of steps to add
            
        Returns:
            Self for method chaining
        """
        self._steps.extend(steps)
        return self
    
    def to_model(self) -> WorkflowModel:
        """Convert to Workflow model."""
        return WorkflowModel(
            name=self.name,
            description=self._description,
            version=self._version,
            steps=[step.to_model() for step in self._steps]
        )
    
    def to_yaml(self) -> str:
        """
        Convert this workflow to YAML.
        
        Returns:
            YAML string representation of the workflow
        """
        return workflow_to_yaml(self.to_model())
    
    def save(self, file_path: str) -> None:
        """
        Save this workflow to a YAML file.
        
        Args:
            file_path: Path to save the file
        """
        with open(file_path, 'w') as f:
            f.write(self.to_yaml())
    
    @classmethod
    def from_yaml(cls, yaml_content: str) -> 'Workflow':
        """
        Create a workflow from YAML content.
        
        Args:
            yaml_content: YAML string
            
        Returns:
            Workflow instance
        """
        model = load_workflow_from_yaml(yaml_content)
        return cls._from_model(model)
    
    @classmethod
    def from_file(cls, file_path: str) -> 'Workflow':
        """
        Load a workflow from a YAML file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Workflow instance
        """
        model = load_workflow_from_file(file_path)
        return cls._from_model(model)
    
    @classmethod
    def _from_model(cls, model: WorkflowModel) -> 'Workflow':
        """
        Create a workflow from a WorkflowModel.
        
        Args:
            model: WorkflowModel instance
            
        Returns:
            Workflow instance
        """
        workflow = cls(model.name)
        workflow.description(model.description)
        workflow.version(model.version)
        
        for step_model in model.steps:
            step = Step(step_model.id)
            step.prompt(step_model.prompt)
            
            for input_model in step_model.inputs:
                step.add_input(
                    name=input_model.name,
                    source=input_model.source,
                    description=input_model.description
                )
            
            for output_model in step_model.outputs:
                step.add_output(
                    name=output_model.name,
                    description=output_model.description
                )
            
            workflow.add_step(step)
        
        return workflow
    
    def __enter__(self) -> 'Workflow':
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        pass
    
    @contextmanager
    def step(self, id: str) -> Step:
        """
        Context manager for creating a step within this workflow.
        
        Args:
            id: Unique identifier for the step
            
        Returns:
            Step instance
        """
        step = Step(id)
        step._parent_workflow = self
        try:
            yield step
        finally:
            if step not in self._steps:
                self.add_step(step) 