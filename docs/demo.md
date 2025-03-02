CLI
- Run a workflow (debate)
- Visualise the results of workflow (riddle)
- Use SDK to define a new workflow

# 5-Minute Demo: "AI Workflow Orchestration in Action"

This demo showcases Orchestrate's key capabilities in a concise 5-minute presentation.

## Setup (30 seconds)
- **Introduction**: "Orchestrate is a tool for defining, executing, and managing AI workflows using YAML or our SDK."
- **Key Message**: "We'll see how Orchestrate makes complex AI workflows manageable and transparent."

## Part 1: Running a Workflow (1.5 minutes)
```bash
# Run the debate workflow with verbose output
python -m src.orchestrate.cli examples/debate.yaml -v
```

**Talking Points:**
- The workflow is structured with multiple steps that build on each other
- Each step has defined inputs (from user or previous steps) and outputs
- The system handles state management between steps automatically
- The `-v` flag saves detailed results including all prompts and responses
- Notice how the debate evolves with pro arguments, con arguments, and rebuttals

## Part 2: Visualizing Results (1 minute)
```bash
# Visualize the results with prompts displayed
python examples/visualize_results.py debate.result.json --show-prompts
```

**Talking Points:**
- The visualization provides a clear view of the workflow execution
- You can inspect prompts and results at each step
- This transparency helps with debugging and refining workflows
- The visualization shows the flow of information between steps
- You can see exactly how each step influenced the final outcome

## Part 3: Using the Composer (1 minute)
```bash
# Generate a workflow using the Composer
python -m src.orchestrate.cli compose "Story Generator" "Create an interactive story with character development and multiple plot branches" -o story_generator.yaml
```

**Talking Points:**
- The Composer automatically generates complete workflows from just a name and description
- This eliminates the need to manually write YAML for common use cases
- The LLM creates a logical sequence of steps with appropriate inputs and outputs
- Generated workflows are immediately usable and follow best practices
- This dramatically speeds up workflow creation for new users
- Let's look at the generated workflow to see its structure

## Part 4: Creating a New Workflow with SDK (1 minute)
```bash
# Show the SDK example
python examples/sdk_example.py
```

**Talking Points:**
- The SDK allows programmatic creation of workflows
- Method chaining creates a clean, readable definition
- This enables dynamic workflow creation based on runtime conditions
- The SDK creates the same workflow as YAML but programmatically
- This approach is ideal for complex workflows or integration with other systems

## Conclusion (30 seconds)

**Key Benefits:**
- Simple YAML definition for static workflows
- Automatic workflow generation with the Composer
- Powerful SDK for programmatic/dynamic creation
- Visualization tools for understanding results
- Flexible execution options (CLI, UI, programmatic)

**Potential Use Cases:**
- Content generation pipelines
- Multi-step reasoning tasks
- Collaborative AI workflows
- Debugging and refining AI prompts