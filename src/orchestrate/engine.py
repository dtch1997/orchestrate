import asyncio
import time
import os
from typing import Dict, Any, Callable, Awaitable, Optional, List, Union

from orchestrate.models import Workflow, WorkflowStep, StepResult, WorkflowResult

# Import the appropriate LLM client based on environment
if os.getenv("ORCHESTRATE_USE_MOCK", "false").lower() == "true":
    from orchestrate.mock_llm import generate_mock_completion as generate_completion
else:
    try:
        from orchestrate.llm import generate_completion
    except ImportError:
        # Fallback to mock if OpenAI is not available
        from orchestrate.mock_llm import generate_mock_completion as generate_completion

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
    
    # In mock mode, we don't need to pass these parameters
    if os.getenv("ORCHESTRATE_USE_MOCK", "false").lower() == "true":
        return await generate_completion(prompt)
    else:
        # Pass model and temperature to the LLM
        return await generate_completion(
            prompt=prompt,
            temperature=temperature,
            system_message=system_message
        )

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
            result = await step_executor(step, context)
            
            # Store the result in context under the step ID
            context[step.id] = result
            
            # Create step result
            execution_time = time.time() - start_time
            step_result = StepResult(
                step_id=step.id,
                result=result,
                execution_time=execution_time
            )
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
                execution_time=execution_time
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
        result = await step_executor(step, context)
        execution_time = time.time() - start_time
        
        return StepResult(
            step_id=step.id,
            result=result,
            execution_time=execution_time
        )
    except Exception as e:
        execution_time = time.time() - start_time
        error_message = f"Error executing step {step.id}: {str(e)}"
        
        return StepResult(
            step_id=step.id,
            result=error_message,
            execution_time=execution_time
        ) 