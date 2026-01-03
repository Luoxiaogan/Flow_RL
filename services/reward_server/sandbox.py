"""
Code Sandbox for Workflow Execution

Provides a secure execution environment for running workflow code.
Supports timeout control and error capture.
"""

import sys
import asyncio
import traceback
import multiprocessing
from io import StringIO
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
from contextlib import redirect_stdout, redirect_stderr

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ExecutionResult:
    """Result of code execution in sandbox"""
    success: bool
    output: Any = None
    stdout: str = ""
    stderr: str = ""
    error: Optional[str] = None
    error_type: Optional[str] = None
    traceback: Optional[str] = None
    execution_time: float = 0.0


def _execute_in_process(
    code: str,
    func_name: str,
    args: Tuple,
    kwargs: Dict,
    result_queue: multiprocessing.Queue,
    allowed_modules: list = None
):
    """
    Execute code in a separate process.

    This function runs in a child process to provide isolation.

    Args:
        code: Python code to execute
        func_name: Function name to call after exec
        args: Positional arguments for the function
        kwargs: Keyword arguments for the function
        result_queue: Queue to put the result
        allowed_modules: List of allowed module names (for future use)
    """
    stdout_capture = StringIO()
    stderr_capture = StringIO()

    try:
        with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
            # Create execution namespace
            namespace = {
                '__builtins__': __builtins__,
                'asyncio': asyncio,
            }

            # Execute the code to define functions/classes
            exec(code, namespace)

            # Get the function to call
            if func_name and func_name in namespace:
                func = namespace[func_name]

                # Check if it's an async function
                if asyncio.iscoroutinefunction(func):
                    # Run async function
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        result = loop.run_until_complete(func(*args, **kwargs))
                    finally:
                        loop.close()
                else:
                    # Run sync function
                    result = func(*args, **kwargs)
            else:
                # Just execute the code without calling a function
                result = None

        result_queue.put({
            'success': True,
            'output': result,
            'stdout': stdout_capture.getvalue(),
            'stderr': stderr_capture.getvalue(),
            'error': None,
            'error_type': None,
            'traceback': None,
        })

    except Exception as e:
        tb = traceback.format_exc()
        result_queue.put({
            'success': False,
            'output': None,
            'stdout': stdout_capture.getvalue(),
            'stderr': stderr_capture.getvalue(),
            'error': str(e),
            'error_type': type(e).__name__,
            'traceback': tb,
        })


class CodeSandbox:
    """
    Sandbox for executing Python code safely.

    Features:
    - Process isolation for security
    - Timeout control
    - Error capture with traceback
    - stdout/stderr capture
    """

    def __init__(
        self,
        default_timeout: float = 30.0,
        allowed_modules: list = None
    ):
        """
        Initialize the sandbox.

        Args:
            default_timeout: Default execution timeout in seconds
            allowed_modules: List of allowed module names (for future use)
        """
        self.default_timeout = default_timeout
        self.allowed_modules = allowed_modules or []

    async def execute(
        self,
        code: str,
        func_name: str = None,
        args: Tuple = (),
        kwargs: Dict = None,
        timeout: float = None
    ) -> ExecutionResult:
        """
        Execute code in the sandbox.

        Args:
            code: Python code to execute
            func_name: Optional function name to call after exec
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            timeout: Execution timeout in seconds

        Returns:
            ExecutionResult with execution details
        """
        import time
        start_time = time.time()

        timeout = timeout or self.default_timeout
        kwargs = kwargs or {}

        # Create a queue for inter-process communication
        result_queue = multiprocessing.Queue()

        # Create and start the process
        process = multiprocessing.Process(
            target=_execute_in_process,
            args=(code, func_name, args, kwargs, result_queue, self.allowed_modules)
        )

        try:
            process.start()

            # Wait for the process with timeout
            process.join(timeout=timeout)

            if process.is_alive():
                # Timeout - terminate the process
                process.terminate()
                process.join(timeout=1.0)

                # Force kill if still alive
                if process.is_alive():
                    process.kill()
                    process.join()

                execution_time = time.time() - start_time
                return ExecutionResult(
                    success=False,
                    error=f"Execution timeout after {timeout} seconds",
                    error_type="TimeoutError",
                    traceback=f"Process terminated due to timeout ({timeout}s)",
                    execution_time=execution_time,
                )

            # Get result from queue
            if not result_queue.empty():
                result_dict = result_queue.get_nowait()
                execution_time = time.time() - start_time
                return ExecutionResult(
                    success=result_dict['success'],
                    output=result_dict['output'],
                    stdout=result_dict['stdout'],
                    stderr=result_dict['stderr'],
                    error=result_dict['error'],
                    error_type=result_dict['error_type'],
                    traceback=result_dict['traceback'],
                    execution_time=execution_time,
                )
            else:
                execution_time = time.time() - start_time
                return ExecutionResult(
                    success=False,
                    error="No result returned from process",
                    error_type="ProcessError",
                    execution_time=execution_time,
                )

        except Exception as e:
            execution_time = time.time() - start_time
            return ExecutionResult(
                success=False,
                error=str(e),
                error_type=type(e).__name__,
                traceback=traceback.format_exc(),
                execution_time=execution_time,
            )
        finally:
            # Cleanup
            if process.is_alive():
                process.terminate()
                process.join(timeout=1.0)
                if process.is_alive():
                    process.kill()

    async def execute_simple(
        self,
        code: str,
        timeout: float = None
    ) -> ExecutionResult:
        """
        Execute simple code without calling a specific function.

        Args:
            code: Python code to execute
            timeout: Execution timeout in seconds

        Returns:
            ExecutionResult with execution details
        """
        return await self.execute(code, func_name=None, timeout=timeout)

    async def execute_workflow(
        self,
        workflow_code: str,
        problem: Dict,
        timeout: float = None
    ) -> ExecutionResult:
        """
        Execute a workflow function on a problem.

        The workflow code should define either:
        - async def solve(problem: dict) -> str
        - def solve(problem: dict) -> str

        Args:
            workflow_code: Workflow Python code
            problem: Problem dictionary to pass to the workflow
            timeout: Execution timeout in seconds

        Returns:
            ExecutionResult with the workflow output
        """
        return await self.execute(
            code=workflow_code,
            func_name="solve",
            args=(problem,),
            timeout=timeout
        )


# Default sandbox instance
_default_sandbox: Optional[CodeSandbox] = None


def get_sandbox(timeout: float = 30.0) -> CodeSandbox:
    """Get or create the default sandbox instance."""
    global _default_sandbox
    if _default_sandbox is None:
        _default_sandbox = CodeSandbox(default_timeout=timeout)
    return _default_sandbox
