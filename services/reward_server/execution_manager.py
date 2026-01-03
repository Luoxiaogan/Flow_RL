"""
Execution Manager for Parallel Workflow Execution

Manages parallel execution of workflows on multiple problems.
Implements All-Reduce pattern: parallel execution, serial aggregation.
Inspired by Flow_RL's WorkflowExecutionManager.
"""

import asyncio
import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from services.reward_server.workflow_executor import (
    WorkflowExecutor,
    WorkflowExecutionResult,
    ProblemResult,
    get_executor
)
from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class BatchExecutionResult:
    """Result of executing a batch of workflows"""
    success: bool
    total_workflows: int
    completed_workflows: int
    results: List[WorkflowExecutionResult] = field(default_factory=list)
    total_execution_time: float = 0.0
    errors: List[str] = field(default_factory=list)


class ExecutionManager:
    """
    Manages parallel workflow execution with safe result aggregation.

    Features:
    - Parallel execution of problems
    - Three-layer timeout control (problem, workflow, batch)
    - Thread-safe result collection with asyncio.Lock
    - All-Reduce pattern: parallel execution, serial aggregation

    Usage:
        manager = ExecutionManager()
        result = await manager.execute_workflow_parallel(
            workflow_code="def solve(problem): return problem['answer']",
            problems=[...],
            benchmark="gsm8k"
        )
    """

    def __init__(
        self,
        executor: WorkflowExecutor = None,
        problem_timeout: float = 60.0,
        workflow_timeout: float = 300.0,
        batch_timeout: float = 600.0,
        max_concurrency: int = 10
    ):
        """
        Initialize the execution manager.

        Args:
            executor: WorkflowExecutor instance
            problem_timeout: Timeout per problem in seconds
            workflow_timeout: Timeout per workflow (all problems) in seconds
            batch_timeout: Timeout for entire batch in seconds
            max_concurrency: Maximum concurrent executions
        """
        self.executor = executor or get_executor(problem_timeout)
        self.problem_timeout = problem_timeout
        self.workflow_timeout = workflow_timeout
        self.batch_timeout = batch_timeout
        self.max_concurrency = max_concurrency

        # Thread-safe result collection
        self._results_lock = asyncio.Lock()
        self._semaphore = asyncio.Semaphore(max_concurrency)

    async def execute_workflow_parallel(
        self,
        workflow_code: str,
        problems: List[Dict[str, Any]],
        benchmark: str,
        timeout: float = None
    ) -> WorkflowExecutionResult:
        """
        Execute a workflow on multiple problems in parallel.

        Args:
            workflow_code: Python code defining the workflow
            problems: List of problem dictionaries
            benchmark: Benchmark name for judging
            timeout: Total timeout in seconds (default: workflow_timeout)

        Returns:
            WorkflowExecutionResult with aggregated results
        """
        timeout = timeout or self.workflow_timeout
        start_time = time.time()

        # Create tasks for parallel execution
        tasks = []
        task_to_problem = {}

        for i, problem in enumerate(problems):
            task = asyncio.create_task(
                self._execute_with_semaphore(
                    workflow_code=workflow_code,
                    problem=problem,
                    benchmark=benchmark,
                    timeout=self.problem_timeout
                )
            )
            tasks.append(task)
            task_to_problem[task] = (i, problem)

        # Wait for all tasks with timeout
        results: List[ProblemResult] = []
        try:
            done, pending = await asyncio.wait(
                tasks,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED
            )

            # Handle timeout - cancel pending tasks
            if pending:
                logger.warning(
                    f"Workflow执行超时: {len(done)}/{len(tasks)} 完成, "
                    f"{len(pending)} 被取消"
                )
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

            # Collect results
            for task in tasks:
                if task in done:
                    try:
                        result = task.result()
                        results.append(result)
                    except Exception as e:
                        idx, problem = task_to_problem[task]
                        results.append(ProblemResult(
                            problem_id=str(problem.get('id', idx)),
                            success=False,
                            correct=False,
                            error=f"Task exception: {str(e)}",
                            error_type="TaskError",
                        ))
                else:
                    # Cancelled due to timeout
                    idx, problem = task_to_problem[task]
                    results.append(ProblemResult(
                        problem_id=str(problem.get('id', idx)),
                        success=False,
                        correct=False,
                        error=f"Cancelled due to timeout ({timeout}s)",
                        error_type="TimeoutError",
                    ))

        except Exception as e:
            logger.error(f"Batch执行异常: {e}")
            # Return failure for all problems
            for i, problem in enumerate(problems):
                results.append(ProblemResult(
                    problem_id=str(problem.get('id', i)),
                    success=False,
                    correct=False,
                    error=str(e),
                    error_type=type(e).__name__,
                ))

        # Aggregate results
        total_time = time.time() - start_time
        return self._aggregate_results(results, total_time)

    async def _execute_with_semaphore(
        self,
        workflow_code: str,
        problem: Dict[str, Any],
        benchmark: str,
        timeout: float
    ) -> ProblemResult:
        """Execute with concurrency control."""
        async with self._semaphore:
            return await self.executor.execute_on_problem(
                workflow_code=workflow_code,
                problem=problem,
                benchmark=benchmark,
                timeout=timeout
            )

    def _aggregate_results(
        self,
        results: List[ProblemResult],
        total_time: float
    ) -> WorkflowExecutionResult:
        """
        Aggregate problem results into workflow result.

        This is the 'Reduce' phase of the All-Reduce pattern.
        """
        total_problems = len(results)
        correct_count = sum(1 for r in results if r.correct)
        failed_count = sum(1 for r in results if not r.success)
        score = correct_count / total_problems if total_problems > 0 else 0.0

        # Determine overall success
        success = failed_count < total_problems

        # Collect first error
        first_error = None
        first_traceback = None
        if not success:
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

    async def execute_batch(
        self,
        workflow_codes: List[str],
        problems_per_workflow: List[List[Dict[str, Any]]],
        benchmarks: List[str],
        timeout: float = None
    ) -> BatchExecutionResult:
        """
        Execute multiple workflows in parallel.

        Args:
            workflow_codes: List of workflow codes
            problems_per_workflow: List of problem lists (one per workflow)
            benchmarks: List of benchmark names (one per workflow)
            timeout: Total batch timeout in seconds

        Returns:
            BatchExecutionResult with all workflow results
        """
        timeout = timeout or self.batch_timeout
        start_time = time.time()

        if len(workflow_codes) != len(problems_per_workflow):
            raise ValueError(
                f"Mismatch: {len(workflow_codes)} workflows vs "
                f"{len(problems_per_workflow)} problem lists"
            )

        if len(workflow_codes) != len(benchmarks):
            raise ValueError(
                f"Mismatch: {len(workflow_codes)} workflows vs "
                f"{len(benchmarks)} benchmarks"
            )

        # Create tasks for each workflow
        tasks = []
        for i, (code, problems, bench) in enumerate(
            zip(workflow_codes, problems_per_workflow, benchmarks)
        ):
            task = asyncio.create_task(
                self.execute_workflow_parallel(
                    workflow_code=code,
                    problems=problems,
                    benchmark=bench,
                    timeout=self.workflow_timeout
                )
            )
            tasks.append(task)

        # Wait for all workflows with batch timeout
        results: List[WorkflowExecutionResult] = []
        errors: List[str] = []

        try:
            done, pending = await asyncio.wait(
                tasks,
                timeout=timeout,
                return_when=asyncio.ALL_COMPLETED
            )

            if pending:
                logger.warning(
                    f"Batch超时: {len(done)}/{len(tasks)} workflows 完成"
                )
                for task in pending:
                    task.cancel()
                await asyncio.gather(*pending, return_exceptions=True)

            for i, task in enumerate(tasks):
                if task in done:
                    try:
                        results.append(task.result())
                    except Exception as e:
                        errors.append(f"Workflow {i}: {str(e)}")
                        results.append(WorkflowExecutionResult(
                            success=False,
                            score=0.0,
                            total_problems=len(problems_per_workflow[i]),
                            correct_count=0,
                            failed_count=len(problems_per_workflow[i]),
                            error=str(e),
                        ))
                else:
                    errors.append(f"Workflow {i}: Timeout")
                    results.append(WorkflowExecutionResult(
                        success=False,
                        score=0.0,
                        total_problems=len(problems_per_workflow[i]),
                        correct_count=0,
                        failed_count=len(problems_per_workflow[i]),
                        error="Batch timeout",
                    ))

        except Exception as e:
            logger.error(f"Batch执行错误: {e}")
            errors.append(str(e))

        total_time = time.time() - start_time
        return BatchExecutionResult(
            success=len(errors) == 0,
            total_workflows=len(workflow_codes),
            completed_workflows=len([r for r in results if r.success]),
            results=results,
            total_execution_time=total_time,
            errors=errors,
        )


# Default manager instance
_default_manager: Optional[ExecutionManager] = None


def get_execution_manager(
    problem_timeout: float = 60.0,
    workflow_timeout: float = 300.0,
    max_concurrency: int = 10
) -> ExecutionManager:
    """Get or create the default execution manager."""
    global _default_manager
    if _default_manager is None:
        _default_manager = ExecutionManager(
            problem_timeout=problem_timeout,
            workflow_timeout=workflow_timeout,
            max_concurrency=max_concurrency
        )
    return _default_manager
