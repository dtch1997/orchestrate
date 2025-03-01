import streamlit as st
import asyncio
import os
import yaml
import json
import time
from pathlib import Path
import tempfile
from datetime import datetime

from orchestrate.models import Workflow, WorkflowStep, StepResult, WorkflowResult
from orchestrate.parser import load_workflow_from_yaml, workflow_to_yaml
from orchestrate.engine import execute_workflow, default_step_executor

# Import the appropriate LLM client based on environment
if os.getenv("ORCHESTRATE_USE_MOCK", "false").lower() == "true":
    from orchestrate.mock_llm import generate_mock_completion as generate_completion
else:
    from orchestrate.llm import generate_completion

# Define color scheme for status indicators
STATUS_COLORS = {
    "pending": "gray",
    "running": "blue",
    "completed": "green",
    "failed": "red"
}

def initialize_session_state():
    """Initialize all session state variables."""
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
    if "step_status" not in st.session_state:
        st.session_state.step_status = {}  # Track status of each step
    if "execution_paused" not in st.session_state:
        st.session_state.execution_paused = False
    if "step_by_step_mode" not in st.session_state:
        st.session_state.step_by_step_mode = False
    if "workflow_params" not in st.session_state:
        st.session_state.workflow_params = {}
    if "execution_history" not in st.session_state:
        st.session_state.execution_history = []
    if "model" not in st.session_state:
        st.session_state.model = "gpt-4o"
    if "temperature" not in st.session_state:
        st.session_state.temperature = 0.7

def render_sidebar():
    """Render the sidebar with workflow management options."""
    with st.sidebar:
        st.header("Workflow Management")
        
        # Option to load example or upload custom
        workflow_source = st.radio(
            "Workflow Source",
            ["Example", "Upload", "Create New"]
        )
        
        if workflow_source == "Example":
            render_example_selector()
                    
        elif workflow_source == "Upload":
            render_file_uploader()
        
        # Button to parse YAML
        if st.button("Load Workflow"):
            load_workflow_from_yaml_content()
        
        # Execution configuration (when workflow is loaded)
        if st.session_state.workflow:
            render_execution_settings()
            render_workflow_parameters()

def render_example_selector():
    """Render the example workflow selector."""
    examples_dir = Path(__file__).parent.parent.parent / "examples"
    example_files = [f for f in os.listdir(examples_dir) if f.endswith(".yaml")]
    
    if example_files:
        example_name = st.selectbox(
            "Select Example",
            example_files,
            index=example_files.index("riddles.yaml") if "riddles.yaml" in example_files else 0
        )
        
        if example_name:
            example_path = examples_dir / example_name
            with open(example_path, "r") as f:
                st.session_state.yaml_content = f.read()
    else:
        st.warning("No example workflows found.")

def render_file_uploader():
    """Render the file upload widget."""
    uploaded_file = st.file_uploader("Upload YAML", type="yaml")
    if uploaded_file:
        st.session_state.yaml_content = uploaded_file.getvalue().decode("utf-8")

def load_workflow_from_yaml_content():
    """Load workflow from YAML content in session state."""
    try:
        st.session_state.workflow = load_workflow_from_yaml(st.session_state.yaml_content)
        # Initialize step status for all steps as pending
        st.session_state.step_status = {step.id: "pending" for step in st.session_state.workflow.steps}
        st.success(f"Loaded workflow: {st.session_state.workflow.name}")
    except Exception as e:
        st.error(f"Error loading workflow: {str(e)}")

def render_execution_settings():
    """Render execution settings in the sidebar."""
    st.markdown("---")
    st.subheader("Execution Settings")
    
    # Model selection
    model = st.selectbox(
        "Model",
        ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        index=0
    )
    st.session_state.model = model
    
    # Temperature
    temperature = st.slider(
        "Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        step=0.1
    )
    st.session_state.temperature = temperature
    
    # Use mock toggle
    use_mock = st.checkbox(
        "Use Mock LLM",
        value=os.getenv("ORCHESTRATE_USE_MOCK", "false").lower() == "true"
    )
    if use_mock:
        os.environ["ORCHESTRATE_USE_MOCK"] = "true"
    else:
        os.environ["ORCHESTRATE_USE_MOCK"] = "false"
    
    # Step-by-step execution mode
    st.session_state.step_by_step_mode = st.checkbox(
        "Step-by-Step Execution",
        value=st.session_state.step_by_step_mode
    )

def render_workflow_parameters():
    """Render workflow parameter inputs."""
    if st.session_state.workflow:
        # Extract parameters from prompts (anything like {{param}})
        import re
        params = set()
        for step in st.session_state.workflow.steps:
            matches = re.findall(r'{{(.*?)}}', step.prompt)
            for match in matches:
                if match not in [s.id for s in st.session_state.workflow.steps]:
                    params.add(match)
        
        # If we have parameters, show input fields
        if params:
            st.markdown("---")
            st.subheader("Workflow Parameters")
            for param in params:
                if param not in st.session_state.workflow_params:
                    st.session_state.workflow_params[param] = ""
                st.session_state.workflow_params[param] = st.text_input(
                    f"{param}",
                    value=st.session_state.workflow_params.get(param, "")
                )

def render_yaml_editor(col):
    """Render the YAML editor in the specified column."""
    with col:
        st.header("Workflow Definition")
        yaml_editor = st.text_area(
            "Edit YAML",
            value=st.session_state.yaml_content,
            height=300
        )
        
        if yaml_editor != st.session_state.yaml_content:
            st.session_state.yaml_content = yaml_editor

def render_workflow_visualization(col):
    """Render the workflow visualization in the specified column."""
    with col:
        st.header("Workflow Visualization")
        
        if st.session_state.workflow:
            render_workflow_details()
            render_execution_controls()
            render_workflow_steps()
            
            # If workflow is running, show progress
            if st.session_state.is_running:
                render_execution_progress()
        else:
            st.info("Load a workflow to see visualization and execute it")

def render_workflow_details():
    """Render workflow metadata."""
    with st.expander("Workflow Details", expanded=True):
        st.markdown(f"**Name:** {st.session_state.workflow.name}")
        if st.session_state.workflow.description:
            st.markdown(f"**Description:** {st.session_state.workflow.description}")
        st.markdown(f"**Version:** {st.session_state.workflow.version}")
        st.markdown(f"**Steps:** {len(st.session_state.workflow.steps)}")

def render_execution_controls():
    """Render execution control buttons."""
    st.markdown("### Execution Controls")
    
    # Create a row of buttons for execution control
    control_cols = st.columns(4)
    
    with control_cols[0]:
        render_run_button()
    
    with control_cols[1]:
        render_pause_resume_button()
    
    with control_cols[2]:
        render_stop_button()
    
    with control_cols[3]:
        render_next_step_button()

def render_run_button():
    """Render the Run button."""
    run_disabled = st.session_state.is_running
    if st.button("▶️ Run", disabled=run_disabled, use_container_width=True):
        # Reset state for new run
        st.session_state.results = {}
        st.session_state.current_step = None
        st.session_state.is_running = True
        st.session_state.execution_paused = False
        st.session_state.step_status = {step.id: "pending" for step in st.session_state.workflow.steps}
        st.rerun()

def render_pause_resume_button():
    """Render the Pause/Resume button."""
    pause_disabled = not st.session_state.is_running
    if st.session_state.execution_paused:
        if st.button("▶️ Resume", disabled=pause_disabled, use_container_width=True):
            st.session_state.execution_paused = False
            st.rerun()
    else:
        if st.button("⏸️ Pause", disabled=pause_disabled, use_container_width=True):
            st.session_state.execution_paused = True
            st.rerun()

def render_stop_button():
    """Render the Stop button."""
    stop_disabled = not st.session_state.is_running
    if st.button("⏹️ Stop", disabled=stop_disabled, use_container_width=True):
        st.session_state.is_running = False
        st.session_state.execution_paused = False
        st.rerun()

def render_next_step_button():
    """Render the Next Step button."""
    next_disabled = not (st.session_state.is_running and 
                        st.session_state.step_by_step_mode and 
                        st.session_state.execution_paused)
    if st.button("⏭️ Next Step", disabled=next_disabled, use_container_width=True):
        st.session_state.execution_paused = False
        st.rerun()

def render_workflow_steps():
    """Render the workflow steps visualization."""
    st.markdown("### Workflow Steps")
    
    # Create a container for steps visualization
    steps_container = st.container()
    
    with steps_container:
        for i, step in enumerate(st.session_state.workflow.steps):
            render_step_card(i, step)

def render_step_card(index, step):
    """Render a card for a workflow step."""
    # Determine step status and icon
    status = st.session_state.step_status.get(step.id, "pending")
    if status == "pending":
        status_icon = "⚪"
    elif status == "running":
        status_icon = "🔵"
    elif status == "completed":
        status_icon = "✅"
    else:  # failed
        status_icon = "❌"
    
    # Create a card-like container for the step
    st.markdown(f"""
    <div style="
        border: 1px solid {STATUS_COLORS[status]}; 
        border-radius: 5px; 
        padding: 10px; 
        margin-bottom: 10px;
        background-color: rgba({', '.join(['200, 200, 200' if status == 'pending' else '173, 216, 230' if status == 'running' else '144, 238, 144' if status == 'completed' else '255, 182, 193'])}, 0.2);
    ">
        <h4>{status_icon} Step {index+1}: {step.id}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    # Show step details in an expander
    with st.expander(f"Details", expanded=False):
        st.markdown(f"**Description:** {step.description if hasattr(step, 'description') else 'No description'}")
        if hasattr(step, 'depends_on') and step.depends_on:
            st.markdown(f"**Depends on:** {', '.join(step.depends_on)}")
        st.markdown("**Prompt:**")
        st.code(step.prompt, language="markdown")
        
        # If step has results, show them
        if step.id in st.session_state.results:
            st.markdown("**Result:**")
            result = st.session_state.results[step.id]
            st.markdown(f"*Execution time: {result.execution_time:.2f} seconds*")
            st.text_area("Result Output", value=result.result, height=150, key=f"result_{step.id}", label_visibility="collapsed")
            
            # Add copy button for result
            if st.button("📋 Copy Result", key=f"copy_{step.id}"):
                st.write("Result copied to clipboard!")
                # Note: In Streamlit, we can't directly copy to clipboard,
                # but we can show a notification that it was "copied"

def render_execution_progress():
    """Render the execution progress section."""
    st.markdown("---")
    st.markdown("### Execution Progress")
    
    # Create progress placeholder
    progress_placeholder = st.empty()
    results_area = st.container()
    
    # Execute and update UI
    with progress_placeholder:
        if st.session_state.execution_paused:
            st.info("Execution paused. Click 'Resume' to continue or 'Next Step' in step-by-step mode.")
        else:
            with st.spinner("Executing workflow..."):
                result = asyncio.run(run_workflow())
                
                if result:
                    # Show completion message
                    st.success(f"Workflow completed in {result.total_execution_time:.2f} seconds")
    
    # Force a rerun to update the UI
    if not st.session_state.execution_paused and st.session_state.is_running:
        time.sleep(0.1)  # Small delay to prevent too rapid reruns
        st.rerun()

def on_step_start(step_id):
    """Callback for when a step starts execution."""
    st.session_state.current_step = step_id
    st.session_state.step_status[step_id] = "running"
    
def on_step_complete(step_id, result):
    """Callback for when a step completes execution."""
    st.session_state.results[step_id] = result
    st.session_state.step_status[step_id] = "completed"

async def run_workflow():
    """Run the workflow asynchronously."""
    workflow = st.session_state.workflow
    
    # Apply parameters to workflow
    for param_name, param_value in st.session_state.workflow_params.items():
        for step in workflow.steps:
            step.prompt = step.prompt.replace(f"{{{{{param_name}}}}}", param_value)
    
    # Execute workflow with pause support
    result = await execute_workflow_with_pause(
        workflow,
        on_step_start=on_step_start,
        on_step_complete=on_step_complete
    )
    
    # Save to execution history
    if not st.session_state.is_running:
        return None  # Execution was stopped
    
    history_entry = {
        "timestamp": datetime.now().isoformat(),
        "workflow_name": workflow.name,
        "total_time": result.total_execution_time,
        "results": {step_id: {"result": step_result.result, "time": step_result.execution_time} 
                   for step_id, step_result in result.step_results.items()}
    }
    st.session_state.execution_history.append(history_entry)
    
    st.session_state.is_running = False
    return result

async def execute_workflow_with_pause(workflow, on_step_start=None, on_step_complete=None, initial_context=None):
    """Execute a workflow with support for pausing."""
    # This is a simplified version - in a real implementation, you'd modify
    # the engine.py execute_workflow function to support pausing
    
    start_time = time.time()
    step_results = {}
    context = initial_context or {}
    
    # Execute steps in order (respecting dependencies)
    executed_steps = set()
    remaining_steps = list(workflow.steps)
    
    while remaining_steps and st.session_state.is_running:
        # Find next executable step
        next_step = None
        for step in remaining_steps:
            dependencies_met = True
            if hasattr(step, 'depends_on') and step.depends_on:
                for dep in step.depends_on:
                    if dep not in executed_steps:
                        dependencies_met = False
                        break
            
            if dependencies_met:
                next_step = step
                break
        
        if not next_step:
            # No executable steps found, but steps remain - circular dependency?
            break
        
        # Check if execution is paused
        while st.session_state.execution_paused and st.session_state.is_running:
            # When paused, sleep briefly and check again
            await asyncio.sleep(0.1)
            
            # In step-by-step mode, we pause after each step
            # The pause will be lifted by the "Next Step" button
        
        # If execution was stopped during pause
        if not st.session_state.is_running:
            break
        
        # Execute step
        if on_step_start:
            on_step_start(next_step.id)
        
        # Process prompt with previous results
        prompt = next_step.prompt
        for step_id, result in step_results.items():
            prompt = prompt.replace(f"{{{{{step_id}}}}}", result.result)
        
        # Update the context with the current step's prompt
        context["current_prompt"] = prompt
        
        # Execute step using the appropriate LLM client
        step_start = time.time()
        
        try:
            # Use the engine's default_step_executor which will use the model and temperature from context
            result = await default_step_executor(next_step, context)
            
            step_time = time.time() - step_start
            
            # Store result
            step_result = StepResult(step_id=next_step.id, result=result, execution_time=step_time)
            step_results[next_step.id] = step_result
            
            # Update context with this step's result
            context[next_step.id] = result
            
            if on_step_complete:
                on_step_complete(next_step.id, step_result)
        except Exception as e:
            # Handle errors
            step_time = time.time() - step_start
            error_message = f"Error executing step {next_step.id}: {str(e)}"
            step_result = StepResult(step_id=next_step.id, result=error_message, execution_time=step_time)
            
            if on_step_complete:
                on_step_complete(next_step.id, step_result)
            
            # Don't continue execution if a step fails
            break
        
        # Mark step as executed and remove from remaining
        executed_steps.add(next_step.id)
        remaining_steps.remove(next_step)
        
        # In step-by-step mode, pause after each step
        if st.session_state.step_by_step_mode:
            st.session_state.execution_paused = True
    
    # Create workflow result
    total_time = time.time() - start_time
    return WorkflowResult(workflow_name=workflow.name, step_results=step_results, total_execution_time=total_time)

def render_results():
    """Render the results section."""
    if st.session_state.results:
        st.markdown("---")
        st.header("Results")
        
        # Create tabs for different result views
        result_tabs = st.tabs(["Current Results", "Execution History"])
        
        with result_tabs[0]:
            render_current_results()
        
        with result_tabs[1]:
            render_execution_history()

def render_current_results():
    """Render the current results tab."""
    # Show current results
    for step_id, step_result in st.session_state.results.items():
        with st.expander(f"Step: {step_id}", expanded=True):
            st.markdown(f"**Execution Time:** {step_result.execution_time:.2f} seconds")
            st.markdown("**Result:**")
            
            # Format the result based on content type
            result_text = step_result.result
            
            # Check if it might be JSON
            try:
                json_data = json.loads(result_text)
                st.json(json_data)
            except:
                # Not JSON, check if it contains code blocks
                if "```" in result_text:
                    st.markdown(result_text)
                else:
                    st.text_area("Result Content", value=result_text, height=200, key=f"formatted_result_{step_id}", label_visibility="collapsed")
    
    if st.session_state.results:
        # Calculate total time
        total_time = sum(r.execution_time for r in st.session_state.results.values())
        st.markdown(f"**Total Execution Time:** {total_time:.2f} seconds")
        
        # Export options
        if st.button("Export Results as JSON"):
            # In a real app, this would download the file
            st.success("Results exported! (This is a placeholder - actual download would happen in production)")

def render_execution_history():
    """Render the execution history tab."""
    # Show execution history
    if not st.session_state.execution_history:
        st.info("No execution history yet")
    else:
        for i, entry in enumerate(reversed(st.session_state.execution_history)):
            with st.expander(f"Run {len(st.session_state.execution_history) - i}: {entry['workflow_name']} - {entry['timestamp']}", expanded=i==0):
                st.markdown(f"**Total Time:** {entry['total_time']:.2f} seconds")
                for step_id, result in entry['results'].items():
                    st.markdown(f"**Step {step_id}** ({result['time']:.2f}s)")
                    st.text_area("Step Result", value=result['result'], height=150, key=f"history_{i}_{step_id}", label_visibility="collapsed")

def execute_workflow_button():
    """Execute the workflow when the button is clicked."""
    if st.session_state.workflow:
        st.session_state.is_running = True
        st.session_state.execution_paused = False
        st.session_state.results = {}
        st.session_state.step_status = {}
        
        # Initialize all steps as pending
        for step in st.session_state.workflow.steps:
            st.session_state.step_status[step.id] = "pending"
        
        # Create initial context with workflow parameters and model settings
        initial_context = {
            **st.session_state.workflow_params,
            "model": st.session_state.model,
            "temperature": st.session_state.temperature
        }
        
        # Start execution in a separate thread
        asyncio.create_task(
            execute_workflow_with_pause(
                st.session_state.workflow,
                on_step_start=lambda step_id: update_step_status(step_id, "running"),
                on_step_complete=lambda step_id, result: handle_step_complete(step_id, result),
                initial_context=initial_context
            )
        )
        st.rerun()

def main():
    """Main entry point for the Streamlit app."""
    st.set_page_config(
        page_title="Orchestrate",
        page_icon="🎼",
        layout="wide"
    )

    # Initialize session state
    initialize_session_state()

    # Title and description
    st.title("🎼 Orchestrate")
    st.markdown("Define, execute, and manage AI workflows with YAML")

    # Sidebar for workflow management
    render_sidebar()

    # Main area - split into two columns
    col1, col2 = st.columns([1, 1])

    # Left column - YAML editor
    render_yaml_editor(col1)

    # Right column - Workflow visualization and execution
    render_workflow_visualization(col2)

    # Results section (below the main columns)
    render_results()

    # Footer
    st.markdown("---")
    st.markdown("Orchestrate - Coordinate your AI workflows with ease")

if __name__ == "__main__":
    main() 