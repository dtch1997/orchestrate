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

Always use pytest as the default testing framework:

```bash
# Install pytest if not already installed
pdm add -d pytest

# Run all tests
pdm run pytest

# Run specific test file
pdm run pytest tests/test_specific.py

# Run with verbose output
pdm run pytest -v
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

## Git Workflow

### Commit Strategy

Make small, incremental commits with clear messages:

```bash
# Good practice for commits
git add specific_file.py
git commit -m "feat: add user authentication to login page"
```

Follow these commit message conventions:
- `feat:` for new features
- `fix:` for bug fixes
- `refactor:` for code refactoring without functionality changes
- `docs:` for documentation updates
- `test:` for adding or updating tests
- `chore:` for routine tasks, dependency updates, etc.

### Development Flow

1. Create a feature branch for each new feature or bug fix
2. Make small, focused commits that do one thing well
3. Write tests before or alongside new code
4. Submit pull requests with comprehensive descriptions 

## Documentation

### Project Updates

All project updates should be documented in `docs/running_notes.md` by default. This file serves as a chronological record of the project's development, with the most recent updates at the top.

When adding a new update:
1. Create a new section with the date and a brief title
2. Document the changes, features, or fixes implemented
3. Include any relevant code examples or usage instructions
4. Note any known issues or limitations

Example format:
```markdown
## March 2025 - Feature Name

### Description
Brief description of the feature or update.

### Implementation Details
- Point 1
- Point 2
- Point 3

### Usage
```bash
# Example command
```

### Known Issues
- Issue 1
- Issue 2
```

### Code Documentation

Use docstrings in all files:

```python
"""
Module docstring explaining the purpose of the file.
"""

def function_name(param1, param2):
    """
    Function docstring explaining what the function does.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
    """
``` 