import asyncio
import unittest
from unittest.mock import AsyncMock, patch
import time

from src.orchestrate.models import Workflow, WorkflowStep, StepResult, WorkflowResult
from src.orchestrate.engine import execute_workflow, execute_step

class TestWorkflowEngine(unittest.TestCase):
    """Test cases for the workflow engine."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a sample workflow
        self.workflow = Workflow(
            name="Test Workflow",
            description="A test workflow",
            steps=[
                WorkflowStep(id="step1", prompt="This is step 1"),
                WorkflowStep(id="step2", prompt="This is step 2"),
                WorkflowStep(id="step3", prompt="This is step 3")
            ]
        )
        
        # Create a mock step executor
        self.mock_executor = AsyncMock()
        self.mock_executor.return_value = "Mock result"
    
    async def async_test_execute_step(self):
        """Test executing a single step."""
        step = self.workflow.steps[0]
        
        # Execute the step with the mock executor
        result = await execute_step(step, {}, self.mock_executor)
        
        # Check that the executor was called with the right arguments
        self.mock_executor.assert_called_once_with(step, {})
        
        # Check the result
        self.assertEqual(result.step_id, step.id)
        self.assertEqual(result.result, "Mock result")
        self.assertGreaterEqual(result.execution_time, 0)
    
    async def async_test_execute_workflow(self):
        """Test executing a complete workflow."""
        # Set up callbacks to track execution
        started_steps = []
        completed_steps = []
        
        def on_step_start(step_id):
            started_steps.append(step_id)
            
        def on_step_complete(step_id, result):
            completed_steps.append(step_id)
        
        # Execute the workflow with the mock executor
        result = await execute_workflow(
            self.workflow,
            step_executor=self.mock_executor,
            on_step_start=on_step_start,
            on_step_complete=on_step_complete
        )
        
        # Check that all steps were started and completed
        self.assertEqual(started_steps, ["step1", "step2", "step3"])
        self.assertEqual(completed_steps, ["step1", "step2", "step3"])
        
        # Check that the executor was called for each step
        self.assertEqual(self.mock_executor.call_count, 3)
        
        # Check the workflow result
        self.assertEqual(result.workflow_name, self.workflow.name)
        self.assertEqual(len(result.step_results), 3)
        self.assertGreaterEqual(result.total_execution_time, 0)
        
        # Check individual step results
        for step in self.workflow.steps:
            self.assertIn(step.id, result.step_results)
            step_result = result.step_results[step.id]
            self.assertEqual(step_result.step_id, step.id)
            self.assertEqual(step_result.result, "Mock result")
    
    async def async_test_execute_workflow_with_error(self):
        """Test workflow execution with an error in one step."""
        # Make the second step fail
        error_executor = AsyncMock()
        error_executor.side_effect = [
            "Result 1",  # First step succeeds
            Exception("Test error"),  # Second step fails
            "Result 3"  # Third step should not be executed
        ]
        
        # Execute the workflow with the error executor
        result = await execute_workflow(
            self.workflow,
            step_executor=error_executor
        )
        
        # Check that only the first two steps were executed
        self.assertEqual(error_executor.call_count, 2)
        
        # Check the workflow result
        self.assertEqual(len(result.step_results), 2)
        self.assertIn("step1", result.step_results)
        self.assertIn("step2", result.step_results)
        self.assertNotIn("step3", result.step_results)
        
        # Check that the error was captured
        self.assertEqual(result.step_results["step1"].result, "Result 1")
        self.assertTrue("Error executing step step2" in result.step_results["step2"].result)
    
    def test_execute_step(self):
        """Run the async test for execute_step."""
        asyncio.run(self.async_test_execute_step())
    
    def test_execute_workflow(self):
        """Run the async test for execute_workflow."""
        asyncio.run(self.async_test_execute_workflow())
    
    def test_execute_workflow_with_error(self):
        """Run the async test for execute_workflow_with_error."""
        asyncio.run(self.async_test_execute_workflow_with_error())

if __name__ == "__main__":
    unittest.main() 