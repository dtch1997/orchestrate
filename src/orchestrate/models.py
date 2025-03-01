from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field

class StepIO(BaseModel):
    """
    Represents an input or output specification for a workflow step.
    
    Attributes:
        name: Name of the input/output
        source: Source of the input (step_id or 'user' for inputs, None for outputs)
        description: Optional description
    """
    name: str
    source: Optional[str] = None
    description: str = ""

class WorkflowStep(BaseModel):
    """
    Represents a single step in a workflow.
    
    Attributes:
        id: Unique identifier for the step
        prompt: The prompt or instruction for this step
        inputs: List of input specifications
        outputs: List of output specifications
    """
    id: str
    prompt: str
    inputs: List[StepIO] = Field(default_factory=list)
    outputs: List[StepIO] = Field(default_factory=list)
    
class Workflow(BaseModel):
    """
    Represents a complete workflow with multiple steps.
    
    Attributes:
        name: Name of the workflow
        description: Optional description of the workflow
        steps: List of workflow steps
    """
    name: str
    description: str = ""
    version: str = ""
    steps: List[WorkflowStep]
    
class StepResult(BaseModel):
    """
    Represents the result of executing a workflow step.
    
    Attributes:
        step_id: ID of the step that was executed
        result: The result data from the step execution
        outputs: Dictionary mapping output names to values
        execution_time: Time taken to execute the step in seconds
        prompt: The full prompt that was sent to the LLM, including variable substitutions
        model: The LLM model used for this step
        temperature: The temperature setting used for this step
        system_message: The system message used for this step
    """
    step_id: str
    result: Any
    outputs: Dict[str, Any] = Field(default_factory=dict)
    execution_time: float
    prompt: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = None
    system_message: Optional[str] = None
    
class WorkflowResult(BaseModel):
    """
    Represents the complete result of a workflow execution.
    
    Attributes:
        workflow_name: Name of the workflow that was executed
        step_results: Results from each step execution
        total_execution_time: Total time taken to execute the workflow
    """
    workflow_name: str
    step_results: Dict[str, StepResult]
    total_execution_time: float 