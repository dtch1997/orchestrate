"""
Test the OpenAI client integration.

This test verifies that the OpenAI client can generate completions.
It requires a valid OpenAI API key in the environment.
"""

import os
import pytest
import pytest_asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Skip tests if OPENAI_API_KEY is not set
pytestmark = [
    pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="OPENAI_API_KEY not set"
    ),
    pytest.mark.asyncio
]

async def test_generate_completion():
    """Test that the OpenAI client can generate completions."""
    from orchestrate.llm import generate_completion
    
    # Generate a completion
    result = await generate_completion(
        prompt="What is the capital of France?",
        temperature=0.7
    )
    
    # Check that we got a non-empty result
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Check that the result contains "Paris" (case insensitive)
    assert "paris" in result.lower()
    
async def test_llm_client_class():
    """Test that the LLMClient class can generate completions."""
    from orchestrate.llm import LLMClient
    
    # Create a client
    client = LLMClient()
    
    # Generate a completion
    result = await client.generate(
        prompt="What is the capital of Italy?",
        temperature=0.7
    )
    
    # Check that we got a non-empty result
    assert result is not None
    assert isinstance(result, str)
    assert len(result) > 0
    
    # Check that the result contains "Rome" (case insensitive)
    assert "rome" in result.lower()

async def test_model_selection():
    """Test that different models can be selected."""
    from orchestrate.llm import LLMClient
    
    # Test with GPT-3.5-turbo
    client_35 = LLMClient(model="gpt-3.5-turbo")
    result_35 = await client_35.generate(
        prompt="What is the capital of Spain?",
        temperature=0.7
    )
    
    # Check that we got a valid result
    assert result_35 is not None
    assert isinstance(result_35, str)
    assert len(result_35) > 0
    assert "madrid" in result_35.lower()
    
    # Test with GPT-4o
    client_4o = LLMClient(model="gpt-4o")
    result_4o = await client_4o.generate(
        prompt="What is the capital of Germany?",
        temperature=0.7
    )
    
    # Check that we got a valid result
    assert result_4o is not None
    assert isinstance(result_4o, str)
    assert len(result_4o) > 0
    assert "berlin" in result_4o.lower()

async def test_temperature_parameter():
    """Test that the temperature parameter affects the output."""
    from orchestrate.llm import LLMClient
    
    # Create a client
    client = LLMClient()
    
    # Generate completions with different temperatures
    # Note: This test is somewhat subjective as temperature affects randomness
    # We're just checking that the API accepts the parameter without error
    
    # Low temperature (more deterministic)
    result_low = await client.generate(
        prompt="Write a short poem about AI.",
        temperature=0.1
    )
    
    # High temperature (more random)
    result_high = await client.generate(
        prompt="Write a short poem about AI.",
        temperature=0.9
    )
    
    # Check that we got valid results
    assert result_low is not None and len(result_low) > 0
    assert result_high is not None and len(result_high) > 0
    
    # The results should be different due to different temperatures
    # This is not guaranteed but highly likely with such different temperatures
    assert result_low != result_high

async def test_workflow_with_openai():
    """Test that a workflow can be executed with the OpenAI integration."""
    from orchestrate.models import Workflow, WorkflowStep
    from orchestrate.engine import execute_workflow
    
    # Make sure we're using the real OpenAI client
    os.environ["ORCHESTRATE_USE_MOCK"] = "false"
    
    # Create a simple workflow
    workflow = Workflow(
        name="Test OpenAI Workflow",
        description="A test workflow using OpenAI",
        steps=[
            WorkflowStep(
                id="generate_question",
                name="Generate a question",
                prompt="Generate a simple trivia question about geography."
            ),
            WorkflowStep(
                id="answer_question",
                name="Answer the question",
                prompt="Answer this geography question: {{generate_question}}"
            )
        ]
    )
    
    # Execute the workflow with model and temperature parameters
    initial_context = {
        "model": "gpt-3.5-turbo",  # Use a faster model for testing
        "temperature": 0.5
    }
    
    result = await execute_workflow(workflow, initial_context=initial_context)
    
    # Check that we got results for both steps
    assert "generate_question" in result.step_results
    assert "answer_question" in result.step_results
    
    # Check that the results are non-empty
    assert result.step_results["generate_question"].result is not None
    assert len(result.step_results["generate_question"].result) > 0
    
    assert result.step_results["answer_question"].result is not None
    assert len(result.step_results["answer_question"].result) > 0
    
    # Check that the second step used the result from the first step
    question = result.step_results["generate_question"].result
    answer = result.step_results["answer_question"].result
    
    # The answer should be related to the question (this is a loose check)
    # We can't check exact content since it's generated by the LLM
    assert len(question) > 10  # Should be a reasonable question
    assert len(answer) > 10    # Should be a reasonable answer 