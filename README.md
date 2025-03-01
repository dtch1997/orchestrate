# Orchestrate 🎼

Orchestrate is a workflow orchestration tool designed to define, execute, and manage multi-step AI-powered workflows using a YAML specification.

## Features

- Define workflows using simple YAML files
- Execute multi-step workflows with a powerful async engine
- Visualize workflow execution in real-time
- Choose from example workflows or create your own

## Installation

```bash
# Install with PDM
pdm install

# Or with pip
pip install .
```

## Quick Start

1. Run the Streamlit app:
   ```bash
   pdm run orchestrate
   ```

2. Open your browser to http://localhost:8501

3. Load an example workflow or create your own

## Workflow Definition

Workflows are defined in YAML with the following structure:

```yaml
name: My Workflow
description: A description of what this workflow does

steps:
  - id: step1
    prompt: What this step should do

  - id: step2
    prompt: What this step should do next
```

Each step has:
- `id`: Unique identifier for the step
- `prompt`: Instructions for what the step should do

## License

MIT
