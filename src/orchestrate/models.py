from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class WorkflowStep(BaseModel):
    """
    Represents a single step in a workflow.
    
    Attributes:
        id: Unique identifier for the step
        prompt: The prompt or instruction for this step
    """
    id: str
    prompt: str
    
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
        execution_time: Time taken to execute the step in seconds
    """
    step_id: str
    result: Any
    execution_time: float
    
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