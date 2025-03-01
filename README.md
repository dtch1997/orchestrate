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
ORCHESTRATE_USE_MOCK=true python -m src.orchestrate.cli examples/debate.yaml -v

# With real OpenAI
python -m src.orchestrate.cli examples/debate.yaml -v
```

## Example Workflows

The `examples/` directory contains several example workflows:

- `marketing.yaml`: Generate a marketing campaign
- `debate.yaml`: Simulate a debate between two AI personas
- `dnd_adventure.yaml`: Create a D&D adventure

## Development

See [Development Instructions](docs/instructions.md) for details on development practices and guidelines.

## License

[MIT License](LICENSE)
