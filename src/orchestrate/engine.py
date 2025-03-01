import asyncio
import time
import os
import re
from typing import Dict, Any, Callable, Awaitable, Optional, List, Union

from orchestrate.models import Workflow, WorkflowStep, StepResult, WorkflowResult, StepIO
from orchestrate.llm import get_llm_client, generate_completion

# Type for step execution function
StepExecutor = Callable[[WorkflowStep, Dict[str, Any]], Awaitable[Any]]

async def default_step_executor(step: WorkflowStep, context: Dict[str, Any]) -> Any:
    """
    Default implementation for executing a workflow step using an LLM.
    
    Args:
        step: The workflow step to execute
        context: Context data that may be used by the step
        
    Returns:
        The result of the step execution (typically a string from the LLM)
    """
    # Process the prompt with context variables
    prompt = step.prompt
    
    # Replace variables in the prompt with values from context
    for key, value in context.items():
        if isinstance(value, str):
            prompt = prompt.replace(f"{{{{{key}}}}}", value)
    
    # Get model and temperature from context if available
    model = context.get("model", os.getenv("OPENAI_MODEL", "gpt-4o"))
    temperature = context.get("temperature", 0.7)
    system_message = context.get("system_message", "You are a helpful assistant in a workflow orchestration system.")
    
    # Store the processed prompt and metadata in context for later use in StepResult
    context["_current_prompt"] = prompt
    context["_current_model"] = model
    context["_current_temperature"] = temperature
    context["_current_system_message"] = system_message
    
    # Use the generate_completion function which handles the client selection internally
    return await generate_completion(
        prompt=prompt,
        temperature=temperature,
        system_message=system_message
    )

def get_input_value(input_spec: StepIO, context: Dict[str, Any]) -> Any:
    """
    Get the value for an input based on its specification.
    
    Args:
        input_spec: The input specification
        context: The current context containing all available values
        
    Returns:
        The value for the input
        
    Raises:
        ValueError: If the input source is not found in the context
    """
    if not input_spec.source:
        return None
        
    if input_spec.source == "user":
        # For user inputs, look for a value with the input name in the context
        if input_spec.name not in context:
            raise ValueError(f"User input '{input_spec.name}' not provided")
        return context[input_spec.name]
    
    # For step outputs, look for the value in the step's outputs
    if input_spec.source not in context:
        raise ValueError(f"Step '{input_spec.source}' not found in context")
        
    step_result = context[input_spec.source]
    
    # If the step result is a StepResult object, get the output with the input name
    if isinstance(step_result, dict) and "outputs" in step_result:
        if input_spec.name not in step_result["outputs"]:
            raise ValueError(f"Output '{input_spec.name}' not found in step '{input_spec.source}'")
        return step_result["outputs"][input_spec.name]
    
    # If the step result is not a StepResult object, return the entire result
    return step_result

def extract_outputs(result: Any, step: WorkflowStep) -> Dict[str, Any]:
    """
    Extract outputs from the step result based on the output specifications.
    
    Args:
        result: The raw result from the step execution
        step: The workflow step with output specifications
        
    Returns:
        Dictionary mapping output names to values
    """
    outputs = {}
    
    # If there are no output specifications, return an empty dictionary
    if not step.outputs:
        return outputs
        
    # If the result is a string, try to extract outputs using regex patterns
    if isinstance(result, str):
        for output in step.outputs:
            # Look for patterns like "Output <name>: <value>" or "<name>: <value>"
            patterns = [
                rf"Output {output.name}:\s*(.*?)(?=\n\n|$)",
                rf"{output.name}:\s*(.*?)(?=\n\n|$)"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, result, re.DOTALL)
                if match:
                    outputs[output.name] = match.group(1).strip()
                    break
    
    # If the result is a dictionary, use it directly
    elif isinstance(result, dict):
        for output in step.outputs:
            if output.name in result:
                outputs[output.name] = result[output.name]
    
    return outputs

async def execute_workflow(
    workflow: Workflow, 
    initial_context: Optional[Dict[str, Any]] = None,
    step_executor: StepExecutor = default_step_executor,
    on_step_start: Optional[Callable[[str], None]] = None,
    on_step_complete: Optional[Callable[[str, Any], None]] = None
) -> WorkflowResult:
    """
    Execute a workflow asynchronously.
    
    Args:
        workflow: The workflow to execute
        initial_context: Initial context data
        step_executor: Function to execute each step
        on_step_start: Callback when a step starts
        on_step_complete: Callback when a step completes
        
    Returns:
        The result of the workflow execution
    """
    context = initial_context or {}
    step_results = {}
    workflow_start_time = time.time()
    
    for step in workflow.steps:
        # Notify step start
        if on_step_start:
            on_step_start(step.id)
            
        # Execute the step
        start_time = time.time()
        try:
            # Prepare step context with inputs
            step_context = {}
            
            # Add global context
            for key, value in context.items():
                if not key.startswith("step_"):
                    step_context[key] = value
            
            # Process inputs
            for input_spec in step.inputs:
                try:
                    step_context[input_spec.name] = get_input_value(input_spec, context)
                except ValueError as e:
                    raise ValueError(f"Error processing input for step {step.id}: {str(e)}")
            
            # Execute the step with the prepared context
            result = await step_executor(step, step_context)
            
            # Extract outputs
            outputs = extract_outputs(result, step)
            
            # Create step result with prompt and metadata
            execution_time = time.time() - start_time
            step_result = StepResult(
                step_id=step.id,
                result=result,
                outputs=outputs,
                execution_time=execution_time,
                prompt=step_context.get("_current_prompt"),
                model=step_context.get("_current_model"),
                temperature=step_context.get("_current_temperature"),
                system_message=step_context.get("_current_system_message")
            )
            
            # Store the result in context under the step ID
            context[step.id] = step_result.model_dump()
            step_results[step.id] = step_result
            
            # Notify step completion
            if on_step_complete:
                on_step_complete(step.id, result)
                
        except Exception as e:
            # Handle step execution errors
            execution_time = time.time() - start_time
            error_message = f"Error executing step {step.id}: {str(e)}"
            
            # Create error step result
            step_result = StepResult(
                step_id=step.id,
                result=error_message,
                execution_time=execution_time,
                prompt=step_context.get("_current_prompt"),
                model=step_context.get("_current_model"),
                temperature=step_context.get("_current_temperature"),
                system_message=step_context.get("_current_system_message")
            )
            step_results[step.id] = step_result
            
            # Notify step completion with error
            if on_step_complete:
                on_step_complete(step.id, error_message)
                
            # Don't continue execution if a step fails
            break
    
    # Calculate total execution time
    total_execution_time = time.time() - workflow_start_time
    
    # Create and return workflow result
    return WorkflowResult(
        workflow_name=workflow.name,
        step_results=step_results,
        total_execution_time=total_execution_time
    )

async def execute_step(
    step: WorkflowStep,
    context: Optional[Dict[str, Any]] = None,
    step_executor: StepExecutor = default_step_executor
) -> StepResult:
    """
    Execute a single workflow step.
    
    Args:
        step: The workflow step to execute
        context: Context data that may be used by the step
        step_executor: Function to execute the step
        
    Returns:
        The result of the step execution
    """
    context = context or {}
    start_time = time.time()
    
    try:
        # Prepare step context with inputs
        step_context = {}
        
        # Add global context
        for key, value in context.items():
            if not key.startswith("step_"):
                step_context[key] = value
        
        # Process inputs
        for input_spec in step.inputs:
            try:
                step_context[input_spec.name] = get_input_value(input_spec, context)
            except ValueError as e:
                raise ValueError(f"Error processing input for step {step.id}: {str(e)}")
        
        # Execute the step with the prepared context
        result = await step_executor(step, step_context)
        
        # Extract outputs
        outputs = extract_outputs(result, step)
        
        execution_time = time.time() - start_time
        
        return StepResult(
            step_id=step.id,
            result=result,
            outputs=outputs,
            execution_time=execution_time,
            prompt=step_context.get("_current_prompt"),
            model=step_context.get("_current_model"),
            temperature=step_context.get("_current_temperature"),
            system_message=step_context.get("_current_system_message")
        )
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = f"Error executing step {step.id}: {str(e)}"
        
        return StepResult(
            step_id=step.id,
            result=error_message,
            execution_time=execution_time,
            prompt=step_context.get("_current_prompt"),
            model=step_context.get("_current_model"),
            temperature=step_context.get("_current_temperature"),
            system_message=step_context.get("_current_system_message")
        ) 