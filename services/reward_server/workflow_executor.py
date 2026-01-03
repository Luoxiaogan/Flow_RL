"""
Workflow Executor

Executes workflow code on test problems and computes accuracy.
Uses the sandbox for safe code execution and benchmark handlers for judging.
"""

import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from services.reward_server.sandbox import CodeSandbox, ExecutionResult, get_sandbox
from src.benchmarks import get_handler
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ProblemResult:
    """Result of executing workflow on a single problem"""
    problem_id: str
    success: bool  # Execution succeeded (no errors)
    correct: bool  # Answer is correct
    model_answer: Optional[str] = None
    expected_answer: Optional[str] = None
    error: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    execution_time: float = 0.0


@dataclass
class WorkflowExecutionResult:
    """Result of executing workflow on multiple problems"""
    success: bool  # All executions succeeded (no fatal errors)
    score: float  # Accuracy (correct / total)
    total_problems: int
    correct_count: int
    failed_count: int
    error: Optional[str] = None  # Global error if any
    traceback: Optional[str] = None
    problem_results: List[ProblemResult] = field(default_factory=list)
    total_execution_time: float = 0.0


class WorkflowExecutor:
    """
    Executes workflow code on test problems.

    Workflow code should define a function:
        async def solve(problem: dict) -> str
    or:
        def solve(problem: dict) -> str

    The problem dict contains:
        - question: The problem question
        - answer: The expected answer (for judging)
        - Any benchmark-specific fields
    """

    def __init__(
        self,
        sandbox: CodeSandbox = None,
        default_timeout: float = 30.0,
        problem_timeout: float = 60.0
    ):
        """
        Initialize the executor.

        Args:
            sandbox: CodeSandbox instance (creates default if None)
            default_timeout: Default timeout per problem in seconds
            problem_timeout: Timeout for each problem execution
        """
        self.sandbox = sandbox or get_sandbox(default_timeout)
        self.default_timeout = default_timeout
        self.problem_timeout = problem_timeout

    async def execute_on_problem(
        self,
        workflow_code: str,
        problem: Dict[str, Any],
        benchmark: str,
        timeout: float = None
    ) -> ProblemResult:
        """
        Execute workflow on a single problem.

        Args:
            workflow_code: Python code defining the workflow
            problem: Problem dictionary with question and answer
            benchmark: Benchmark name for judging
            timeout: Execution timeout in seconds

        Returns:
            ProblemResult with execution details
        """
        timeout = timeout or self.problem_timeout
        problem_id = problem.get('id', problem.get('idx', 'unknown'))
        start_time = time.time()

        try:
            # Execute the workflow in sandbox
            result: ExecutionResult = await self.sandbox.execute_workflow(
                workflow_code=workflow_code,
                problem=problem,
                timeout=timeout
            )

            execution_time = time.time() - start_time

            if not result.success:
                # Execution failed
                return ProblemResult(
                    problem_id=str(problem_id),
                    success=False,
                    correct=False,
                    error=result.error,
                    error_type=result.error_type,
                    traceback=result.traceback,
                    execution_time=execution_time,
                )

            # Get the model answer
            model_answer = result.output
            if model_answer is None:
                model_answer = ""
            if not isinstance(model_answer, str):
                model_answer = str(model_answer)

            # Judge the answer using benchmark handler
            expected_answer = problem.get('answer', problem.get('ground_truth', ''))
            try:
                handler = get_handler(benchmark)
                ground_truth_data = {
                    'question': problem.get('question', ''),
                    'answer': expected_answer,
                    **problem  # Include all problem fields
                }
                judge_result = handler.judge(model_answer, ground_truth_data)
                correct = judge_result.get('correct', False) if isinstance(judge_result, dict) else bool(judge_result)
            except Exception as e:
                # If judging fails, mark as incorrect
                logger.warning(f"Judging failed for problem {problem_id}: {e}")
                correct = False

            return ProblemResult(
                problem_id=str(problem_id),
                success=True,
                correct=correct,
                model_answer=model_answer,
                expected_answer=str(expected_answer),
                execution_time=execution_time,
            )

        except Exception as e:
            import traceback as tb
            execution_time = time.time() - start_time
            return ProblemResult(
                problem_id=str(problem_id),
                success=False,
                correct=False,
                error=str(e),
                error_type=type(e).__name__,
                traceback=tb.format_exc(),
                execution_time=execution_time,
            )

    async def execute_on_problems(
        self,
        workflow_code: str,
        problems: List[Dict[str, Any]],
        benchmark: str,
        timeout_per_problem: float = None
    ) -> WorkflowExecutionResult:
        """
        Execute workflow on multiple problems sequentially.

        Note: For parallel execution, use ExecutionManager instead.

        Args:
            workflow_code: Python code defining the workflow
            problems: List of problem dictionaries
            benchmark: Benchmark name for judging
            timeout_per_problem: Timeout per problem in seconds

        Returns:
            WorkflowExecutionResult with aggregated results
        """
        start_time = time.time()
        results: List[ProblemResult] = []
        correct_count = 0
        failed_count = 0

        for problem in problems:
            result = await self.execute_on_problem(
                workflow_code=workflow_code,
                problem=problem,
                benchmark=benchmark,
                timeout=timeout_per_problem
            )
            results.append(result)

            if result.correct:
                correct_count += 1
            if not result.success:
                failed_count += 1

        total_time = time.time() - start_time
        total_problems = len(problems)
        score = correct_count / total_problems if total_problems > 0 else 0.0

        # Determine overall success (at least some executions succeeded)
        success = failed_count < total_problems

        # Collect first error if all failed
        first_error = None
        first_traceback = None
        if not success and results:
            for r in results:
                if r.error:
                    first_error = r.error
                    first_traceback = r.traceback
                    break

        return WorkflowExecutionResult(
            success=success,
            score=score,
            total_problems=total_problems,
            correct_count=correct_count,
            failed_count=failed_count,
            error=first_error,
            traceback=first_traceback,
            problem_results=results,
            total_execution_time=total_time,
        )


# Default executor instance
_default_executor: Optional[WorkflowExecutor] = None


def get_executor(timeout: float = 60.0) -> WorkflowExecutor:
    """Get or create the default executor instance."""
    global _default_executor
    if _default_executor is None:
        _default_executor = WorkflowExecutor(problem_timeout=timeout)
    return _default_executor
