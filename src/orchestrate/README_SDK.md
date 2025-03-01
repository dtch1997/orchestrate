# Orchestrate SDK

The Orchestrate SDK provides a fluid interface for building workflows programmatically in Python. This is an alternative to the YAML-based approach, offering more flexibility and better IDE support.

## Installation

The SDK is included as part of the Orchestrate package:

```bash
pip install orchestrate
```

## Basic Usage

### Method Chaining Approach

```python
from orchestrate.sdk import Workflow, Step

# Create a new workflow
workflow = (
    Workflow("My Workflow")
    .description("A simple workflow example")
    .version("1.0")
)

# Add steps with method chaining
workflow.add_step(
    Step("first_step")
    .prompt("Generate a story about {{topic}}")
    .add_input("topic", source="user", description="The topic for the story")
    .add_output("story", description="The generated story")
)

workflow.add_step(
    Step("second_step")
    .prompt("Summarize the following story: {{story}}")
    .add_input("story", source="first_step", description="The story to summarize")
    .add_output("summary", description="The summary of the story")
)

# Save to YAML
workflow.save("my_workflow.yaml")
```

### Context Manager Approach

```python
from orchestrate.sdk import Workflow

# Create a workflow using context managers
with Workflow("My Workflow") as workflow:
    workflow.description("A simple workflow example")
    workflow.version("1.0")
    
    # First step
    with workflow.step("first_step") as step1:
        step1.prompt("Generate a story about {{topic}}")
        step1.add_input("topic", source="user", description="The topic for the story")
        step1.add_output("story", description="The generated story")
    
    # Second step
    with workflow.step("second_step") as step2:
        step2.prompt("Summarize the following story: {{story}}")
        step2.add_input("story", source="first_step", description="The story to summarize")
        step2.add_output("summary", description="The summary of the story")

# Save to YAML
workflow.save("my_workflow.yaml")
```

## Loading Existing Workflows

You can load existing YAML workflows and modify them programmatically:

```python
from orchestrate.sdk import Workflow

# Load from a file
workflow = Workflow.from_file("existing_workflow.yaml")

# Add a new step
workflow.add_step(
    Step("new_step")
    .prompt("Analyze the sentiment of: {{text}}")
    .add_input("text", source="user")
    .add_output("sentiment")
)

# Save back to YAML
workflow.save("modified_workflow.yaml")
```

## Converting Between Models and SDK Objects

The SDK provides methods to convert between the internal models and SDK builder objects:

```python
from orchestrate.sdk import Workflow
from orchestrate.models import Workflow as WorkflowModel

# Convert SDK object to model
workflow = Workflow("Example")
model = workflow.to_model()

# Convert model to SDK object
workflow = Workflow._from_model(model)
```

## API Reference

### Workflow

- `__init__(name: str)`: Initialize a workflow with a name
- `description(text: str) -> Workflow`: Set the workflow description
- `version(version: str) -> Workflow`: Set the workflow version
- `add_step(step: Step) -> Workflow`: Add a step to the workflow
- `add_steps(steps: List[Step]) -> Workflow`: Add multiple steps to the workflow
- `to_model() -> WorkflowModel`: Convert to a WorkflowModel
- `to_yaml() -> str`: Convert to YAML string
- `save(file_path: str) -> None`: Save to a YAML file
- `from_yaml(yaml_content: str) -> Workflow`: Create from YAML content (class method)
- `from_file(file_path: str) -> Workflow`: Load from a YAML file (class method)
- `step(id: str) -> Step`: Context manager for creating a step

### Step

- `__init__(id: str)`: Initialize a step with an ID
- `prompt(text: str) -> Step`: Set the prompt text
- `add_input(name: str, source: Optional[str] = None, description: str = "") -> Step`: Add an input
- `add_output(name: str, description: str = "") -> Step`: Add an output
- `to_model() -> WorkflowStepModel`: Convert to a WorkflowStepModel

### Input

- `__init__(name: str, source: Optional[str] = None, description: str = "")`: Initialize an input
- `to_model() -> StepIOModel`: Convert to a StepIOModel

### Output

- `__init__(name: str, description: str = "")`: Initialize an output
- `to_model() -> StepIOModel`: Convert to a StepIOModel

## Future Enhancements

- Conditional execution capabilities (branching, if/else logic)
- Helper methods for common workflow patterns
- Enhanced type safety and validation
- Integration with workflow execution engine 