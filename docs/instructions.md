# Development Instructions for Orchestrate

## Package Management

Always use PDM for package management. Never use pip directly.

```bash
# To add a new package
pdm add <package-name>

# To add a development dependency
pdm add -d <package-name>

# To install all dependencies
pdm install

# To update dependencies
pdm update
```

## Environment Setup

1. The project uses environment variables stored in a `.env` file in the project root.
2. Use `python-dotenv` to load these variables (already integrated with PDM).

## Running the Application

### Development Mode

```bash
# Set PYTHONPATH and run with mock LLM
PYTHONPATH=. ORCHESTRATE_USE_MOCK=true streamlit run src/orchestrate/app.py

# Run with real OpenAI integration
PYTHONPATH=. streamlit run demo.py
```

### Testing

```bash
# Run unit tests
pdm run python -m unittest discover tests
```

## Code Structure

- `src/orchestrate/` - Main package
- `examples/` - Example workflows
- `tests/` - Unit tests
- `demo.py` - Entry point for demo with OpenAI integration

## Import Structure

Use absolute imports in all files:

```python
# Correct
from orchestrate.models import Workflow

# Incorrect - causes issues with Streamlit
from .models import Workflow
``` 