# Workflow Results Visualizer

The Workflow Results Visualizer is a command-line tool for visualizing the outputs of all steps in an Orchestrate workflow in an end-to-end way.

## Features

- Display workflow execution results in a focused, easy-to-read way
- Show the flow of data between steps by focusing on step outputs
- Format different output types appropriately (text, JSON, etc.)
- View prompts used for each step (optional)
- View full results of each step (optional)
- View full outputs without truncation (optional)
- Display detailed metadata about each step (optional)
- Automatically find and load associated workflow definitions

## Installation

The visualizer is included with the Orchestrate package. If you have Orchestrate installed, you already have access to the visualizer.

```bash
# Install from source
pip install -e .
```

## Usage

### Command-line Interface

```bash
# Basic usage - shows only step outputs (truncated to 100 characters)
orchestrate-visualize path/to/workflow.result.json

# Show verbose output (includes model and temperature)
orchestrate-visualize path/to/workflow.result.json -v

# Show prompts used for each step
orchestrate-visualize path/to/workflow.result.json -p

# Show full results of each step (not just outputs)
orchestrate-visualize path/to/workflow.result.json -r

# Show full outputs without truncation
orchestrate-visualize path/to/workflow.result.json -f

# Show all details (verbose, prompts, full results, and full outputs)
orchestrate-visualize path/to/workflow.result.json -v -p -r -f

# Specify a workflow file explicitly
orchestrate-visualize path/to/workflow.result.json -w path/to/workflow.yaml

# Adjust the output width
orchestrate-visualize path/to/workflow.result.json --width 120
```

### Programmatic Usage

You can also use the visualizer programmatically in your Python code:

```python
from orchestrate import load_result_from_file, load_workflow_from_file, visualize_workflow_result

# Load the result file
result = load_result_from_file("path/to/workflow.result.json")

# Optionally load the workflow file for better context
workflow = load_workflow_from_file("path/to/workflow.yaml")

# Visualize the result (only showing outputs by default, truncated to 100 characters)
visualize_workflow_result(
    result,
    workflow=workflow
)

# Visualize with all details
visualize_workflow_result(
    result,
    workflow=workflow,
    verbose=True,
    show_prompts=True,
    show_full_results=True,
    show_full_outputs=True,
    width=100
)
```

## Example Output

### Default Output (Only Outputs, Truncated)

```
================================================================================
Workflow: Riddle Generator
Total Execution Time: 5.23s
Steps: 2
================================================================================

Step: generate_riddle
Execution Time: 3.12s

Outputs:
  riddle: I speak without a mouth and hear without ears. I have no body, but I come alive with the wind. What am I?

--------------------------------------------------------------------------------

Step: solve_riddle
Execution Time: 2.11s

Outputs:
  solution: an echo

--------------------------------------------------------------------------------
```

### Full Output (With -v -p -r -f flags)

```
================================================================================
Workflow: Riddle Generator
Total Execution Time: 5.23s
Steps: 2
================================================================================

Step: generate_riddle
Execution Time: 3.12s

Prompt:
  Generate a riddle about the following topic: echo

Result:
  I speak without a mouth and hear without ears. I have no body, but I come alive
  with the wind. What am I?

Outputs:
  riddle:
    I speak without a mouth and hear without ears. I have no body, but I come alive
    with the wind. What am I?

Model: gpt-4o
Temperature: 0.7

--------------------------------------------------------------------------------

Step: solve_riddle
Execution Time: 2.11s

Prompt:
  Solve the following riddle: I speak without a mouth and hear without ears. I have no body, but I come alive
  with the wind. What am I?

Result:
  The answer to the riddle "I speak without a mouth and hear without ears. I have
  no body, but I come alive with the wind" is "an echo".
  
  An echo:
  - Speaks (repeats sounds) without having a mouth
  - Hears (receives sounds) without having ears
  - Has no physical body
  - Comes alive (becomes noticeable) with the wind or in open spaces where sound can travel

Outputs:
  solution:
    an echo

Model: gpt-4o
Temperature: 0.7

--------------------------------------------------------------------------------
```

## Advanced Features

### Filtering Results

You can focus on specific steps by using the workflow file to determine the step order and relationships.

### Exporting Results

The visualizer currently displays results to the terminal, but you can redirect the output to a file:

```bash
orchestrate-visualize path/to/workflow.result.json > workflow_report.txt
```

## Future Enhancements

- Interactive mode with step navigation
- Visual representation of data flow between steps
- Support for comparing results across multiple workflow runs
- HTML report generation
- Integration with the Orchestrate web UI 