import streamlit as st
import asyncio
import os
import yaml
import time
from pathlib import Path
import tempfile

from orchestrate.models import Workflow, WorkflowStep
from orchestrate.parser import load_workflow_from_yaml, workflow_to_yaml
from orchestrate.engine import execute_workflow

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(
        page_title="Orchestrate",
        page_icon="🎼",
        layout="wide"
    )

    # Session state initialization
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    if "results" not in st.session_state:
        st.session_state.results = {}
    if "current_step" not in st.session_state:
        st.session_state.current_step = None
    if "yaml_content" not in st.session_state:
        st.session_state.yaml_content = ""
    if "is_running" not in st.session_state:
        st.session_state.is_running = False

    # Title and description
    st.title("🎼 Orchestrate")
    st.markdown("Define, execute, and manage AI workflows with YAML")

    # Sidebar for workflow management
    with st.sidebar:
        st.header("Workflow Management")
        
        # Option to load example or upload custom
        workflow_source = st.radio(
            "Workflow Source",
            ["Example", "Upload", "Create New"]
        )
        
        if workflow_source == "Example":
            examples_dir = Path(__file__).parent.parent.parent / "examples"
            example_files = [f for f in os.listdir(examples_dir) if f.endswith(".yaml")]
            
            if example_files:
                example_name = st.selectbox(
                    "Select Example",
                    example_files
                )
                
                if example_name:
                    example_path = examples_dir / example_name
                    with open(example_path, "r") as f:
                        st.session_state.yaml_content = f.read()
            else:
                st.warning("No example workflows found.")
                    
        elif workflow_source == "Upload":
            uploaded_file = st.file_uploader("Upload YAML", type="yaml")
            if uploaded_file:
                st.session_state.yaml_content = uploaded_file.getvalue().decode("utf-8")
        
        # Button to parse YAML
        if st.button("Load Workflow"):
            try:
                st.session_state.workflow = load_workflow_from_yaml(st.session_state.yaml_content)
                st.success(f"Loaded workflow: {st.session_state.workflow.name}")
            except Exception as e:
                st.error(f"Error loading workflow: {str(e)}")

    # Main area - split into two columns
    col1, col2 = st.columns([1, 1])

    # Left column - YAML editor
    with col1:
        st.header("Workflow Definition (YAML)")
        yaml_editor = st.text_area(
            "Edit YAML",
            value=st.session_state.yaml_content,
            height=400
        )
        
        if yaml_editor != st.session_state.yaml_content:
            st.session_state.yaml_content = yaml_editor

    # Right column - Workflow visualization and execution
    with col2:
        st.header("Workflow Execution")
        
        if st.session_state.workflow:
            st.subheader(f"Workflow: {st.session_state.workflow.name}")
            if st.session_state.workflow.description:
                st.markdown(st.session_state.workflow.description)
            
            # Display steps
            st.markdown("### Steps")
            for i, step in enumerate(st.session_state.workflow.steps):
                with st.expander(f"Step {i+1}: {step.id}"):
                    st.markdown(f"**Prompt:** {step.prompt}")
            
            # Execute button
            if st.button("Execute Workflow"):
                st.session_state.results = {}
                st.session_state.current_step = None
                st.session_state.is_running = True
                
                # Create progress placeholder
                progress_placeholder = st.empty()
                results_area = st.container()
                
                # Define callbacks
                def on_step_start(step_id):
                    st.session_state.current_step = step_id
                    
                def on_step_complete(step_id, result):
                    st.session_state.results[step_id] = result
                
                # Run the workflow asynchronously
                async def run_workflow():
                    workflow = st.session_state.workflow
                    result = await execute_workflow(
                        workflow,
                        on_step_start=on_step_start,
                        on_step_complete=on_step_complete
                    )
                    st.session_state.is_running = False
                    return result
                
                # Execute and update UI
                with progress_placeholder:
                    with st.spinner("Executing workflow..."):
                        result = asyncio.run(run_workflow())
                
                # Show results
                with results_area:
                    st.markdown("### Results")
                    for step_id, step_result in result.step_results.items():
                        with st.expander(f"Step: {step_id}"):
                            st.markdown(f"**Execution Time:** {step_result.execution_time:.2f} seconds")
                            st.markdown("**Result:**")
                            st.text_area("", value=step_result.result, height=200, key=f"result_{step_id}")
                    
                    st.markdown(f"**Total Execution Time:** {result.total_execution_time:.2f} seconds")
        else:
            st.info("Load a workflow to see details and execute it")

    # Footer
    st.markdown("---")
    st.markdown("Orchestrate - Coordinate your AI workflows with ease")

if __name__ == "__main__":
    main() 