"""
Reward Client for Training

Async HTTP client for communicating with the Reward Server.
Used by the generation manager to execute workflows and get rewards.
"""

import asyncio
import aiohttp
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result from executing a workflow"""
    success: bool
    score: float
    error: Optional[str] = None
    traceback: Optional[str] = None
    total_problems: int = 0
    correct_count: int = 0
    failed_problems: List[Dict[str, Any]] = field(default_factory=list)
    problem_results: List[Dict[str, Any]] = field(default_factory=list)


class RewardClient:
    """
    Async HTTP client for the Reward Server.

    Usage:
        client = RewardClient("http://localhost:7788")
        result = await client.execute_workflow(
            workflow_code="def solve(p): return p['answer']",
            test_problems=[{"question": "...", "answer": "..."}],
            benchmark="gsm8k"
        )
    """

    def __init__(
        self,
        server_url: str,
        timeout: float = 300.0,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """
        Initialize the reward client.

        Args:
            server_url: URL of the reward server (e.g., http://localhost:7788)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Delay between retries in seconds
        """
        self.server_url = server_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._session: Optional[aiohttp.ClientSession] = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self):
        """Close the HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

    async def health_check(self) -> bool:
        """Check if the reward server is healthy."""
        try:
            session = await self._get_session()
            async with session.get(f"{self.server_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("status") == "healthy"
                return False
        except Exception as e:
            logger.warning(f"Health check failed: {e}")
            return False

    async def execute_workflow(
        self,
        workflow_code: str,
        test_problems: List[Dict[str, Any]],
        benchmark: str = "gsm8k",
        timeout: int = 60
    ) -> ExecutionResult:
        """
        Execute a workflow on test problems.

        Args:
            workflow_code: Python code defining the workflow
            test_problems: List of test problems
            benchmark: Benchmark name for judging
            timeout: Per-problem timeout in seconds

        Returns:
            ExecutionResult with execution details
        """
        request_data = {
            "workflow_code": workflow_code,
            "test_problems": test_problems,
            "benchmark": benchmark,
            "timeout": timeout
        }

        for attempt in range(self.max_retries):
            try:
                session = await self._get_session()
                async with session.post(
                    f"{self.server_url}/execute_workflow",
                    json=request_data
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return ExecutionResult(
                            success=data.get("success", False),
                            score=data.get("score", 0.0),
                            error=data.get("error"),
                            traceback=data.get("traceback"),
                            total_problems=data.get("details", {}).get("total", 0),
                            correct_count=data.get("details", {}).get("correct", 0),
                            failed_problems=data.get("details", {}).get("failed", []),
                            problem_results=data.get("problem_results", [])
                        )
                    else:
                        error_text = await response.text()
                        logger.warning(
                            f"Workflow execution failed (attempt {attempt + 1}): "
                            f"status={response.status}, error={error_text}"
                        )

            except asyncio.TimeoutError:
                logger.warning(
                    f"Workflow execution timeout (attempt {attempt + 1})"
                )
            except Exception as e:
                logger.warning(
                    f"Workflow execution error (attempt {attempt + 1}): {e}"
                )

            # Wait before retry
            if attempt < self.max_retries - 1:
                await asyncio.sleep(self.retry_delay * (attempt + 1))

        # All retries failed
        return ExecutionResult(
            success=False,
            score=0.0,
            error=f"Failed after {self.max_retries} attempts",
            total_problems=len(test_problems),
            correct_count=0
        )

    async def compute_reward(
        self,
        task_id: str,
        question: str,
        ground_truth: str,
        model_answer: str,
        benchmark: str = "gsm8k"
    ) -> Dict[str, Any]:
        """
        Compute reward for a single answer (uses the simple /reward endpoint).

        Args:
            task_id: Task identifier
            question: Original question
            ground_truth: Expected answer
            model_answer: Model's answer
            benchmark: Benchmark name

        Returns:
            Dict with success, score, and breakdown
        """
        request_data = {
            "task_id": task_id,
            "question": question,
            "ground_truth": ground_truth,
            "model_answer": model_answer,
            "benchmark": benchmark,
            "metadata": {}
        }

        try:
            session = await self._get_session()
            async with session.post(
                f"{self.server_url}/reward",
                json=request_data
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    error_text = await response.text()
                    return {
                        "success": False,
                        "score": 0.0,
                        "error": f"HTTP {response.status}: {error_text}"
                    }
        except Exception as e:
            return {
                "success": False,
                "score": 0.0,
                "error": str(e)
            }

    async def execute_batch(
        self,
        workflows: List[str],
        problems_per_workflow: List[List[Dict[str, Any]]],
        benchmarks: List[str],
        timeout: int = 60
    ) -> List[ExecutionResult]:
        """
        Execute multiple workflows in parallel.

        Args:
            workflows: List of workflow codes
            problems_per_workflow: List of problem lists (one per workflow)
            benchmarks: List of benchmark names
            timeout: Per-problem timeout in seconds

        Returns:
            List of ExecutionResults
        """
        if len(workflows) != len(problems_per_workflow):
            raise ValueError("Mismatch between workflows and problems count")

        if len(workflows) != len(benchmarks):
            raise ValueError("Mismatch between workflows and benchmarks count")

        # Create tasks for parallel execution
        tasks = []
        for code, problems, bench in zip(workflows, problems_per_workflow, benchmarks):
            task = self.execute_workflow(
                workflow_code=code,
                test_problems=problems,
                benchmark=bench,
                timeout=timeout
            )
            tasks.append(task)

        # Execute all in parallel
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Convert exceptions to failed results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append(ExecutionResult(
                    success=False,
                    score=0.0,
                    error=str(result),
                    total_problems=len(problems_per_workflow[i]),
                    correct_count=0
                ))
            else:
                final_results.append(result)

        return final_results

    async def __aenter__(self):
        """Async context manager entry."""
        await self._get_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


# Convenience function for one-off executions
async def execute_workflow(
    workflow_code: str,
    test_problems: List[Dict[str, Any]],
    benchmark: str = "gsm8k",
    server_url: str = "http://localhost:7788",
    timeout: int = 60
) -> ExecutionResult:
    """
    Execute a workflow and return the result.

    This is a convenience function for one-off executions.
    For multiple executions, use RewardClient directly.
    """
    async with RewardClient(server_url) as client:
        return await client.execute_workflow(
            workflow_code=workflow_code,
            test_problems=test_problems,
            benchmark=benchmark,
            timeout=timeout
        )
