import yaml
from typing import Dict, Any, Optional
from pathlib import Path

from .models import Workflow, WorkflowStep

def load_workflow_from_yaml(yaml_content: str) -> Workflow:
    """
    Parse YAML content into a Workflow object.
    
    Args:
        yaml_content: String containing YAML workflow definition
        
    Returns:
        Workflow object
        
    Raises:
        ValueError: If the YAML content is invalid or missing required fields
    """
    try:
        data = yaml.safe_load(yaml_content)
        
        # Validate required fields
        if not isinstance(data, dict):
            raise ValueError("YAML content must be a dictionary")
        
        if "name" not in data:
            raise ValueError("Workflow must have a name")
            
        if "steps" not in data or not isinstance(data["steps"], list):
            raise ValueError("Workflow must have a list of steps")
        
        # Extract workflow metadata
        name = data.get("name")
        description = data.get("description", "")
        
        # Parse steps
        steps_data = data.get("steps", [])
        steps = []
        
        for i, step_data in enumerate(steps_data):
            if not isinstance(step_data, dict):
                raise ValueError(f"Step {i} must be a dictionary")
                
            if "id" not in step_data:
                raise ValueError(f"Step {i} must have an id")
                
            if "prompt" not in step_data:
                raise ValueError(f"Step {i} must have a prompt")
                
            steps.append(WorkflowStep(**step_data))
        
        return Workflow(name=name, description=description, steps=steps)
    except yaml.YAMLError as e:
        raise ValueError(f"Failed to parse YAML: {str(e)}")
    except Exception as e:
        raise ValueError(f"Failed to parse workflow: {str(e)}")

def load_workflow_from_file(file_path: str) -> Workflow:
    """
    Load workflow from a YAML file.
    
    Args:
        file_path: Path to the YAML file
        
    Returns:
        Workflow object
        
    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file content is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
        
    with open(file_path, "r") as f:
        yaml_content = f.read()
        
    return load_workflow_from_yaml(yaml_content)

def workflow_to_yaml(workflow: Workflow) -> str:
    """
    Convert a Workflow object to a YAML string.
    
    Args:
        workflow: Workflow object to convert
        
    Returns:
        YAML string representation of the workflow
    """
    workflow_dict = workflow.model_dump()
    return yaml.dump(workflow_dict, sort_keys=False) 