"""
Test Workflow Execution Components

Tests for:
- Sandbox code execution
- Workflow executor
- Execution manager
"""

import asyncio
import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestSandbox:
    """Test the code sandbox."""

    @pytest.mark.asyncio
    async def test_simple_execution(self):
        """Test simple code execution."""
        from services.reward_server.sandbox import CodeSandbox

        sandbox = CodeSandbox(default_timeout=10.0)

        code = """
def solve(problem):
    return str(int(problem['a']) + int(problem['b']))
"""
        result = await sandbox.execute(
            code=code,
            func_name="solve",
            args=({"a": 1, "b": 2},)
        )

        assert result.success
        assert result.output == "3"
        assert result.error is None

    @pytest.mark.asyncio
    async def test_async_execution(self):
        """Test async function execution."""
        from services.reward_server.sandbox import CodeSandbox

        sandbox = CodeSandbox(default_timeout=10.0)

        code = """
import asyncio

async def solve(problem):
    await asyncio.sleep(0.1)
    return str(int(problem['x']) * 2)
"""
        result = await sandbox.execute(
            code=code,
            func_name="solve",
            args=({"x": 5},)
        )

        assert result.success
        assert result.output == "10"

    @pytest.mark.asyncio
    async def test_timeout(self):
        """Test execution timeout."""
        from services.reward_server.sandbox import CodeSandbox

        sandbox = CodeSandbox(default_timeout=1.0)

        code = """
import time

def solve(problem):
    time.sleep(10)  # Should timeout
    return "done"
"""
        result = await sandbox.execute(
            code=code,
            func_name="solve",
            args=({},),
            timeout=1.0
        )

        assert not result.success
        assert "timeout" in result.error.lower()

    @pytest.mark.asyncio
    async def test_error_capture(self):
        """Test error and traceback capture."""
        from services.reward_server.sandbox import CodeSandbox

        sandbox = CodeSandbox(default_timeout=10.0)

        code = """
def solve(problem):
    return 1 / 0  # ZeroDivisionError
"""
        result = await sandbox.execute(
            code=code,
            func_name="solve",
            args=({},)
        )

        assert not result.success
        assert result.error_type == "ZeroDivisionError"
        assert "ZeroDivisionError" in result.traceback


class TestWorkflowExecutor:
    """Test the workflow executor."""

    @pytest.mark.asyncio
    async def test_execute_on_problem(self):
        """Test executing workflow on a single problem."""
        from services.reward_server.workflow_executor import WorkflowExecutor

        executor = WorkflowExecutor(problem_timeout=10.0)

        workflow_code = """
def solve(problem):
    # Simple answer extraction
    return problem.get('answer', '')
"""

        problem = {
            "id": "test_1",
            "question": "What is 1+1?",
            "answer": "2"
        }

        result = await executor.execute_on_problem(
            workflow_code=workflow_code,
            problem=problem,
            benchmark="gsm8k"
        )

        assert result.success
        # Note: correctness depends on benchmark handler

    @pytest.mark.asyncio
    async def test_execute_on_problems(self):
        """Test executing workflow on multiple problems."""
        from services.reward_server.workflow_executor import WorkflowExecutor

        executor = WorkflowExecutor(problem_timeout=10.0)

        workflow_code = """
def solve(problem):
    return problem.get('answer', '')
"""

        problems = [
            {"id": "1", "question": "Q1", "answer": "A1"},
            {"id": "2", "question": "Q2", "answer": "A2"},
            {"id": "3", "question": "Q3", "answer": "A3"},
        ]

        result = await executor.execute_on_problems(
            workflow_code=workflow_code,
            problems=problems,
            benchmark="gsm8k"
        )

        assert result.total_problems == 3
        assert len(result.problem_results) == 3


class TestExecutionManager:
    """Test the execution manager."""

    @pytest.mark.asyncio
    async def test_parallel_execution(self):
        """Test parallel workflow execution."""
        from services.reward_server.execution_manager import ExecutionManager

        manager = ExecutionManager(
            problem_timeout=10.0,
            workflow_timeout=30.0,
            max_concurrency=5
        )

        workflow_code = """
def solve(problem):
    return problem.get('answer', '')
"""

        problems = [
            {"id": str(i), "question": f"Q{i}", "answer": f"A{i}"}
            for i in range(5)
        ]

        result = await manager.execute_workflow_parallel(
            workflow_code=workflow_code,
            problems=problems,
            benchmark="gsm8k"
        )

        assert result.total_problems == 5
        assert len(result.problem_results) == 5


class TestPromptBuilder:
    """Test the prompt builder."""

    def test_generation_prompt(self):
        """Test building generation prompt."""
        from training.rollout.prompt_builder import PromptBuilder

        builder = PromptBuilder()

        prompt = builder.build_generation_prompt(
            task_description="Solve math problems",
            benchmark_name="gsm8k",
            example_problems=[
                {"question": "What is 2+2?", "answer": "4"}
            ]
        )

        assert "gsm8k" in prompt
        assert "Solve math problems" in prompt
        assert "2+2" in prompt

    def test_repair_prompt(self):
        """Test building repair prompt."""
        from training.rollout.prompt_builder import PromptBuilder

        builder = PromptBuilder()

        prompt = builder.build_repair_prompt(
            base_prompt="Original prompt",
            previous_code="def solve(): pass",
            error_message="NameError: undefined variable",
            traceback="Traceback: ..."
        )

        assert "Previous Attempt" in prompt
        assert "def solve(): pass" in prompt
        assert "NameError" in prompt

    def test_code_extraction(self):
        """Test extracting code from response."""
        from training.rollout.prompt_builder import PromptBuilder

        builder = PromptBuilder()

        response = """
Here's the solution:

```python
def solve(problem):
    return "answer"
```

This should work.
"""
        code = builder.extract_code_from_response(response)

        assert code is not None
        assert "def solve" in code
        assert "return" in code


def run_tests():
    """Run all tests."""
    import subprocess
    result = subprocess.run(
        ["python", "-m", "pytest", __file__, "-v", "--tb=short"],
        cwd=project_root
    )
    return result.returncode


if __name__ == "__main__":
    # Quick manual test
    print("Running quick sandbox test...")

    async def quick_test():
        from services.reward_server.sandbox import CodeSandbox

        sandbox = CodeSandbox(default_timeout=10.0)

        code = """
def solve(problem):
    question = problem['question']
    # Simple: extract number and double it
    import re
    nums = re.findall(r'\\d+', question)
    if nums:
        return str(int(nums[0]) * 2)
    return "0"
"""
        result = await sandbox.execute(
            code=code,
            func_name="solve",
            args=({"question": "What is 5 times 2?"},)
        )

        print(f"Success: {result.success}")
        print(f"Output: {result.output}")
        print(f"Error: {result.error}")
        print(f"Time: {result.execution_time:.2f}s")

    asyncio.run(quick_test())
    print("\nQuick test passed!")
