# Orchestrate

Define, execute, and manage AI workflows with YAML.

## Overview

Orchestrate is a workflow management system designed to coordinate AI workflows using YAML for definition and a Streamlit UI for interaction. It allows you to create multi-step AI workflows and execute them with either a mock LLM client (for testing) or the real OpenAI API.

## Features

- Define workflows in YAML with a simple, human-readable syntax
- Execute workflows step by step with progress tracking
- Use either a mock LLM client or the real OpenAI API
- Interactive Streamlit UI for workflow management
- Command-line interface for batch processing
- Enhanced result history with full prompt storage and inspection
- Support for input/output specifications between workflow steps
- **NEW: Composer feature to automatically generate workflows using an LLM**
- **NEW: Compiler to validate workflows and generate specifications**

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/orchestrate.git
   cd orchestrate
   ```

2. Install dependencies using PDM:
   ```bash
   pdm install
   ```

3. Set up your environment:
   ```bash
   cp .env.example .env
   ```
   
4. Edit the `.env` file and add your OpenAI API key.

## Usage

### Running with Mock LLM (for testing)

To run the application with the mock LLM client (no API key required):

```bash
PYTHONPATH=. ORCHESTRATE_USE_MOCK=true streamlit run src/orchestrate/app.py
```

### Running with OpenAI Integration

To run the application with the real OpenAI API:

```bash
python demo.py
```

### Command Line Interface

You can also run workflows from the command line:

```bash
# With mock LLM
ORCHESTRATE_USE_MOCK=true python -m src.orchestrate.cli run examples/debate.yaml -v

# With real OpenAI
python -m src.orchestrate.cli run examples/debate.yaml -v
```

### Using the Composer

The Composer feature allows you to automatically generate workflows using an LLM based on a name and description:

```bash
# Generate a workflow and save it to a file
python -m src.orchestrate.cli compose "Marketing Campaign" "Generate a marketing campaign for a new product launch" -o marketing.yaml

# Generate a workflow and print it to the console
python -m src.orchestrate.cli compose "D&D Adventure" "Create a D&D adventure with character generation and storytelling"
```

You can also use the dedicated composer CLI:

```bash
python -m src.orchestrate.cli_compose "Marketing Campaign" "Generate a marketing campaign for a new product launch" -o marketing.yaml
```

### Using the Compiler

The Compiler validates workflows and generates specifications that summarize inputs and outputs:

```bash
# Validate a workflow and print the specification
python -m src.orchestrate.cli compile examples/debate.yaml

# Output the specification in JSON format
python -m src.orchestrate.cli compile examples/debate.yaml --json

# Save the specification to a file
python -m src.orchestrate.cli compile examples/debate.yaml -o debate_spec.json --json
```

You can also use the dedicated compiler CLI:

```bash
python -m src.orchestrate.cli_compile examples/debate.yaml
```

The compiler checks that:
- All inputs are either provided by the user or by outputs of previous steps
- All inputs are used somewhere in the step
- The workflow follows a valid sequence of steps

### Viewing Result History and Prompts

When running workflows, Orchestrate now stores the full prompts and metadata for each step:

#### In the UI:
- The execution history tab shows all previous workflow runs
- Each step result includes the original prompt, model, temperature, and system message
- This information helps with debugging and refining your workflows

#### In the CLI:
- Use the `-v` (verbose) flag to save detailed results including prompts
- Results are saved as JSON files with the same name as your workflow file
- Example: `examples/debate.yaml.result.json`

#### Programmatically:
```python
from orchestrate.engine import execute_workflow
from orchestrate.parser import load_workflow_from_file

# Load and execute a workflow
workflow = load_workflow_from_file("examples/debate.yaml")
result = await execute_workflow(workflow)

# Access the full prompt for a specific step
step_id = "generate_topic"
step_result = result.step_results[step_id]
print(f"Prompt: {step_result.prompt}")
print(f"Model: {step_result.model}")
print(f"Temperature: {step_result.temperature}")
print(f"Result: {step_result.result}")
```

## Example Workflows

The `examples/` directory contains several example workflows:

- `marketing.yaml`: Generate a marketing campaign
- `debate.yaml`: Simulate a debate between two AI personas
- `dnd_adventure.yaml`: Create a D&D adventure
- `riddles.yaml`: Generate and solve riddles

## Development

See [Development Instructions](docs/instructions.md) for details on development practices and guidelines.

## License

[MIT License](LICENSE)
