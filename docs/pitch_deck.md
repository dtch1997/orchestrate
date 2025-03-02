---
marp: true
theme: default
paginate: true
backgroundColor: #fff
style: |
  section {
    font-size: 1.5rem;
  }
  h1 {
    font-size: 2.5rem;
    color: #333;
  }
  h2 {
    font-size: 2rem;
    color: #0066cc;
  }
  img {
    display: block;
    margin: 0 auto;
  }
  code {
    background-color: #f0f0f0;
    padding: 0.2em 0.4em;
    border-radius: 3px;
  }
  pre {
    background-color: #f8f8f8;
    border-radius: 5px;
    padding: 1em;
    margin: 0.5em 0;
    overflow: auto;
  }
---

<!-- _class: lead -->
# Orchestrate
## AI Workflow Orchestration for Agents

---

# 1. Problem Statement

- **Complexity of AI Workflows**: LLM agents need to perform multi-step tasks but lack structured ways to coordinate complex processes
- **Prompt Engineering Challenges**: Building reliable, repeatable AI workflows requires careful prompt design and state management
- **Lack of Transparency**: Black-box AI systems make debugging and improvement difficult
- **Integration Difficulties**: Connecting AI capabilities with existing systems is often ad-hoc and brittle

---

# 2. Workflow

Simple YAML-based workflow configuration that is:

- **Declarative**: Describes what to do, not how to do it
- **Structured**: Clear organization of steps, inputs, and outputs

This makes it portable, readable, and easy to version-control. 

---

# 3. Workflow Definition: The Basics

Every workflow starts with a name and description:

```yaml
name: "AI Debate"
description: "Orchestrate a debate between two AI personas on a given topic"
```

---

# 4. Workflow Definition: Adding Steps

Steps define the sequence of operations in a workflow:

```yaml
name: "AI Debate"
description: "Orchestrate a debate between two AI personas on a given topic"

steps:
  - id: "generate_topic"
    prompt: "Generate an interesting debate topic. If the user provided a topic suggestion, use that as inspiration: {{topic}}"
```

Each step has:
- A unique identifier
- A prompt template for the LLM
- Optional placeholder variables (e.g., `{{topic}}`)

---

# 5. Workflow Definition: Inputs and Outputs

Connecting steps with inputs and outputs:

```yaml
steps:
  - id: "generate_topic"
    prompt: "Generate an interesting debate topic. If the user provided a topic suggestion, use that as inspiration: {{topic}}"
    inputs:
      - name: "topic"
        description: "Optional topic suggestion for the debate"
        source: "user"
    outputs:
      - name: "debate_topic"
        description: "The generated topic for debate"
```

- **Inputs**: Define where data comes from (user or previous steps)
- **Outputs**: Define what data this step produces for later steps

---

# 6. Workflow Definition: Complete Example

```yaml
name: "AI Debate"
description: "Orchestrate a debate between two AI personas on a given topic"

steps:
  - id: "generate_topic"
    prompt: "Generate an interesting debate topic. If the user provided a topic suggestion, use that as inspiration: {{topic}}"
    inputs:
      - name: "topic"
        description: "Optional topic suggestion for the debate"
        source: "user"
    outputs:
      - name: "debate_topic"
        description: "The generated topic for debate"
  
  - id: "pro_arguments"
    prompt: "You are an expert debater. Generate compelling arguments in favor of {{debate_topic}}"
    inputs:
      - name: "debate_topic"
        source: "generate_topic"
    outputs:
      - name: "pro_args"
        description: "Arguments in favor of the topic"
```

---

# 7. Workflow Definition: Data Flow

The complete workflow shows how data flows between steps:

```yaml
  - id: "con_arguments"
    prompt: "You are an expert debater. Generate compelling arguments against {{debate_topic}}"
    inputs:
      - name: "debate_topic"
        source: "generate_topic"
    outputs:
      - name: "con_args"
        description: "Arguments against the topic"
  
  - id: "debate_summary"
    prompt: "Summarize the debate between these two positions:\n\nPro: {{pro_args}}\n\nCon: {{con_args}}"
    inputs:
      - name: "pro_args"
        source: "pro_arguments"
      - name: "con_args"
        source: "con_arguments"
    outputs:
      - name: "debate_summary"
        description: "Summary and analysis of the debate"
```

- Each step builds on previous steps
- Clear data dependencies make the workflow easy to understand

---

# 8. Demo: Running a Workflow

```bash
# Run the debate workflow with verbose output
python -m src.orchestrate.cli run examples/debate.yaml -v
```

- Workflow is structured with multiple steps that build on each other
- Each step has defined inputs (from user or previous steps) and outputs
- System handles state management between steps automatically
- The `-v` flag saves detailed results including all prompts and responses

---

# 9. Demo: Generating Workflows with Composer

```bash
# Generate a workflow using the Composer
python -m src.orchestrate.cli compose "Story Generator" \
  "Create an interactive story with character development" \
  -o story_generator.yaml
```

- Automatically generates complete workflows from just a name and description
- Eliminates the need to manually write YAML for common use cases
- LLM creates a logical sequence of steps with appropriate inputs and outputs
- Generated workflows are immediately usable and follow best practices

---

# 10. Demo: Validating Workflows with Compiler

```bash
# Validate a workflow and generate a specification
python -m src.orchestrate.cli compile examples/debate.yaml
```

- Validates that all inputs are properly sourced (user or previous steps)
- Ensures all inputs are used in the step's prompt
- Checks for proper sequencing of steps
- Generates a specification summarizing inputs and outputs
- Provides clear error messages for invalid workflows

---

# 11. Technical Architecture

- **Workflow Specification is Key**: The YAML format is the core innovation, not the engine
- **Lightweight Engine**: Simple asyncio-based execution of workflow steps
- **OpenAI Integration**: Currently uses OpenAI API for its structured output capabilities
- **Separation of Concerns**: The workflow definition is completely independent of the execution engine
- **Modular Components**: Parser, composer, and compiler work with the workflow specification

---

<!-- _class: lead -->
# Thank You!

## Summary
- **Orchestrate** provides a simple YAML format for defining AI workflows
- Workflows connect steps with clear input/output relationships
- Our tools help you create, validate, and run complex AI processes

## Questions?

---

# 12. Competitive Advantages

- **AI-Native**: Designed specifically for LLM agent interaction
- **Low Barrier to Entry**: No complex programming required
- **Transparency**: Full visibility into the AI decision process
- **Validation**: Compiler ensures workflows are valid before execution
- **Flexibility**: Works for simple tasks and complex multi-agent workflows

---

# 13. Market Opportunity

- **Growing Agent Ecosystem**: As LLM agents become more capable, they need better tools
- **Enterprise AI Adoption**: Companies need structured ways to deploy AI workflows
- **Developer Productivity**: Reduces time spent on prompt engineering and workflow design
- **AI Safety & Governance**: Provides audit trails and oversight for AI systems

---

# 14. Business Model

- **Open Core**: Basic functionality open source, premium features for enterprise
- **Hosted Service**: Cloud-based workflow execution and management
- **Enterprise Support**: Custom integrations and dedicated support
- **Workflow Marketplace**: Revenue sharing for workflow creators

---

# 15. Traction & Roadmap

**Current State**:
- Core functionality complete
- Composer feature for automatic workflow generation
- Compiler for workflow validation and specification
- Fluid SDK for programmatic workflow creation

**Next Steps**:
- Agent-specific API for direct integration
- Multi-agent workflow coordination
- Workflow versioning and A/B testing
- Integration with popular agent frameworks

---

# 16. Demo: Programmatic Workflow Creation

```python
from orchestrate.sdk import Workflow, Step

workflow = (Workflow("Debate")
    .description("Orchestrate a debate between two AI personas")
    .add_step(Step("generate_topic")
        .prompt("Generate a debate topic: {{topic}}")
        .input("topic", source="user")
        .output("debate_topic"))
    .add_step(Step("pro_arguments")
        .prompt("Generate pro arguments for {{debate_topic}}")
        .input("debate_topic", source="generate_topic")
        .output("pro_args")))
```

- SDK allows programmatic creation of workflows
- Method chaining creates a clean, readable definition
- Enables dynamic workflow creation based on runtime conditions

---

<!-- _class: lead -->
# 17. Call to Action

- **For Developers**: Try Orchestrate for your next AI project
- **For Enterprises**: Schedule a demo of agent-driven workflow automation
- **For AI Researchers**: Contribute to the open-source ecosystem
- **For Investors**: Join us in building the infrastructure for the agent economy

---

# Key Messaging Points

1. **"Orchestrate is the missing infrastructure for LLM agents"** - Providing the structure agents need to perform complex tasks reliably

2. **"From natural language to working workflows in seconds"** - The Composer bridges the gap between agent intent and executable processes

3. **"Transparent AI you can trust"** - Full visibility into every step of the AI decision process

4. **"AI building AI"** - Agents can create, modify, and improve workflows without human intervention

5. **"The operating system for the agent economy"** - Providing the foundation for agent-driven automation at scale 