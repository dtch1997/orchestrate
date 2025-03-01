#!/usr/bin/env python3
"""
Example demonstrating the Orchestrate SDK for building workflows programmatically.

This example creates the same debate workflow as in examples/debate.yaml,
but using the fluid SDK interface instead of YAML.
"""

import sys
import os
import textwrap
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.orchestrate.sdk import Workflow, Step


def create_debate_workflow_method_chaining():
    """Create a debate workflow using method chaining."""
    
    # Create a new workflow
    workflow = (
        Workflow("AI Debate")
        .description("Orchestrate a debate between two AI personas on a given topic")
        .version("1.0")
    )
    
    # Add setup step
    workflow.add_step(
        Step("setup_topic")
        .prompt(
            "Moderate a debate on topic: {{topic}}. Write a compelling thesis statement "
            "for the topic. Also define the format and rules for the debate."
        )
        .add_input("topic", source="user", description="Optional topic suggestion for the debate")
        .add_output("debate_topic", description="The finalized thesis statement for the debate")
        .add_output("debate_format", description="The format and rules for the debate")
    )
    
    # Add pro argument step
    workflow.add_step(
        Step("pro_argument")
        .prompt(textwrap.dedent("""
            Generate an argument in favor of the topic. Present a well-reasoned
            case with supporting evidence and logical reasoning.
            
            Topic: {{debate_topic}}
            Format: {{debate_format}}
        """).strip())
        .add_input("debate_topic", source="setup_topic", description="The topic being debated")
        .add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
        .add_output("pro_position", description="The argument in favor of the topic")
    )
    
    # Add con argument step
    workflow.add_step(
        Step("con_argument")
        .prompt(textwrap.dedent("""
            Generate an argument against the topic. Present a well-reasoned
            counter-argument with supporting evidence and logical reasoning.
            
            Topic: {{debate_topic}}
            Format: {{debate_format}}
            Pro Argument: {{pro_position}}
        """).strip())
        .add_input("debate_topic", source="setup_topic", description="The topic being debated")
        .add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
        .add_input("pro_position", source="pro_argument", description="The argument in favor of the topic")
        .add_output("con_position", description="The argument against the topic")
    )
    
    # Add pro rebuttal step
    workflow.add_step(
        Step("pro_rebuttal")
        .prompt(textwrap.dedent("""
            Respond to the counter-argument with a rebuttal. Address specific points
            raised in the counter-argument and strengthen your position.
            
            Topic: {{debate_topic}}
            Format: {{debate_format}}
            Initial Pro Argument: {{pro_position}}
            Con Argument: {{con_position}}
        """).strip())
        .add_input("debate_topic", source="setup_topic", description="The topic being debated")
        .add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
        .add_input("pro_position", source="pro_argument", description="The initial argument in favor of the topic")
        .add_input("con_position", source="con_argument", description="The argument against the topic")
        .add_output("pro_rebuttal_text", description="The rebuttal to the con argument")
    )
    
    # Add con rebuttal step
    workflow.add_step(
        Step("con_rebuttal")
        .prompt(textwrap.dedent("""
            Respond to the pro rebuttal with a final counter. Address specific points
            and provide a compelling closing argument.
            
            Topic: {{debate_topic}}
            Format: {{debate_format}}
            Initial Con Argument: {{con_position}}
            Pro Rebuttal: {{pro_rebuttal_text}}
        """).strip())
        .add_input("debate_topic", source="setup_topic", description="The topic being debated")
        .add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
        .add_input("con_position", source="con_argument", description="The initial argument against the topic")
        .add_input("pro_rebuttal_text", source="pro_rebuttal", description="The rebuttal to the con argument")
        .add_output("con_rebuttal_text", description="The final counter to the pro rebuttal")
    )
    
    # Add summary step
    workflow.add_step(
        Step("summary")
        .prompt(textwrap.dedent("""
            Summarize the debate, highlighting the key points from both sides.
            Provide an analysis of the strengths and weaknesses of each argument.
            
            Topic: {{debate_topic}}
            Format: {{debate_format}}
            Pro Argument: {{pro_position}}
            Con Argument: {{con_position}}
            Pro Rebuttal: {{pro_rebuttal_text}}
            Con Rebuttal: {{con_rebuttal_text}}
        """).strip())
        .add_input("debate_topic", source="setup_topic", description="The topic being debated")
        .add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
        .add_input("pro_position", source="pro_argument", description="The initial argument in favor of the topic")
        .add_input("con_position", source="con_argument", description="The initial argument against the topic")
        .add_input("pro_rebuttal_text", source="pro_rebuttal", description="The rebuttal to the con argument")
        .add_input("con_rebuttal_text", source="con_rebuttal", description="The final counter to the pro rebuttal")
        .add_output("debate_summary", description="Summary and analysis of the debate")
    )
    
    return workflow


def create_debate_workflow_context_manager():
    """Create a debate workflow using context managers."""
    
    # Create a new workflow using context manager
    with Workflow("AI Debate") as workflow:
        workflow.description("Orchestrate a debate between two AI personas on a given topic")
        workflow.version("1.0")
        
        # Setup topic step
        with workflow.step("setup_topic") as setup:
            setup.prompt(
                "Moderate a debate on topic: {{topic}}. Write a compelling thesis statement "
                "for the topic. Also define the format and rules for the debate."
            )
            setup.add_input("topic", source="user", description="Optional topic suggestion for the debate")
            setup.add_output("debate_topic", description="The finalized thesis statement for the debate")
            setup.add_output("debate_format", description="The format and rules for the debate")
        
        # Pro argument step
        with workflow.step("pro_argument") as pro:
            pro.prompt(textwrap.dedent("""
                Generate an argument in favor of the topic. Present a well-reasoned
                case with supporting evidence and logical reasoning.
                
                Topic: {{debate_topic}}
                Format: {{debate_format}}
            """).strip())
            pro.add_input("debate_topic", source="setup_topic", description="The topic being debated")
            pro.add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
            pro.add_output("pro_position", description="The argument in favor of the topic")
        
        # Con argument step
        with workflow.step("con_argument") as con:
            con.prompt(textwrap.dedent("""
                Generate an argument against the topic. Present a well-reasoned
                counter-argument with supporting evidence and logical reasoning.
                
                Topic: {{debate_topic}}
                Format: {{debate_format}}
                Pro Argument: {{pro_position}}
            """).strip())
            con.add_input("debate_topic", source="setup_topic", description="The topic being debated")
            con.add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
            con.add_input("pro_position", source="pro_argument", description="The argument in favor of the topic")
            con.add_output("con_position", description="The argument against the topic")
        
        # Pro rebuttal step
        with workflow.step("pro_rebuttal") as pro_rebuttal:
            pro_rebuttal.prompt(textwrap.dedent("""
                Respond to the counter-argument with a rebuttal. Address specific points
                raised in the counter-argument and strengthen your position.
                
                Topic: {{debate_topic}}
                Format: {{debate_format}}
                Initial Pro Argument: {{pro_position}}
                Con Argument: {{con_position}}
            """).strip())
            pro_rebuttal.add_input("debate_topic", source="setup_topic", description="The topic being debated")
            pro_rebuttal.add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
            pro_rebuttal.add_input("pro_position", source="pro_argument", description="The initial argument in favor of the topic")
            pro_rebuttal.add_input("con_position", source="con_argument", description="The argument against the topic")
            pro_rebuttal.add_output("pro_rebuttal_text", description="The rebuttal to the con argument")
        
        # Con rebuttal step
        with workflow.step("con_rebuttal") as con_rebuttal:
            con_rebuttal.prompt(textwrap.dedent("""
                Respond to the pro rebuttal with a final counter. Address specific points
                and provide a compelling closing argument.
                
                Topic: {{debate_topic}}
                Format: {{debate_format}}
                Initial Con Argument: {{con_position}}
                Pro Rebuttal: {{pro_rebuttal_text}}
            """).strip())
            con_rebuttal.add_input("debate_topic", source="setup_topic", description="The topic being debated")
            con_rebuttal.add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
            con_rebuttal.add_input("con_position", source="con_argument", description="The initial argument against the topic")
            con_rebuttal.add_input("pro_rebuttal_text", source="pro_rebuttal", description="The rebuttal to the con argument")
            con_rebuttal.add_output("con_rebuttal_text", description="The final counter to the pro rebuttal")
        
        # Summary step
        with workflow.step("summary") as summary:
            summary.prompt(textwrap.dedent("""
                Summarize the debate, highlighting the key points from both sides.
                Provide an analysis of the strengths and weaknesses of each argument.
                
                Topic: {{debate_topic}}
                Format: {{debate_format}}
                Pro Argument: {{pro_position}}
                Con Argument: {{con_position}}
                Pro Rebuttal: {{pro_rebuttal_text}}
                Con Rebuttal: {{con_rebuttal_text}}
            """).strip())
            summary.add_input("debate_topic", source="setup_topic", description="The topic being debated")
            summary.add_input("debate_format", source="setup_topic", description="The format and rules for the debate")
            summary.add_input("pro_position", source="pro_argument", description="The initial argument in favor of the topic")
            summary.add_input("con_position", source="con_argument", description="The initial argument against the topic")
            summary.add_input("pro_rebuttal_text", source="pro_rebuttal", description="The rebuttal to the con argument")
            summary.add_input("con_rebuttal_text", source="con_rebuttal", description="The final counter to the pro rebuttal")
            summary.add_output("debate_summary", description="Summary and analysis of the debate")
    
    return workflow


def main():
    """Main function to demonstrate the SDK."""
    
    # Create workflows using both approaches
    workflow1 = create_debate_workflow_method_chaining()
    workflow2 = create_debate_workflow_context_manager()
    
    # Save to YAML files
    output_dir = Path(__file__).parent / "output"
    output_dir.mkdir(exist_ok=True)
    
    workflow1.save(str(output_dir / "debate_method_chaining.yaml"))
    workflow2.save(str(output_dir / "debate_context_manager.yaml"))
    
    print(f"Saved workflow YAML files to {output_dir}")
    
    # Print the YAML for the context manager version
    print("\nWorkflow YAML (context manager version):")
    print(workflow2.to_yaml())


if __name__ == "__main__":
    main() 