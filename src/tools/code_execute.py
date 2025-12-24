"""
Code Execute Tool for New_Flow_RL

在安全沙箱中执行 Python 代码。
支持两种执行模式：
1. 本地沙箱（默认）
2. SandboxFusion API（外部服务）

SandboxFusion API 文档：
https://bytedance.github.io/SandboxFusion/docs/docs/get-started
"""

import sys
import time
import traceback
import requests
from io import StringIO
from typing import Any, Dict, Optional
from contextlib import contextmanager
import signal
import threading

from src.tools.base import PydanticTool, ToolResult
from src.tools.models import CodeExecuteInput, CodeExecuteOutput
from src.core.logger import get_logger

logger = get_logger(__name__)


class SandboxFusionClient:
    """
    SandboxFusion API 客户端。

    提供与 ByteDance SandboxFusion 服务的交互接口。

    API Endpoints:
        - POST /run_code: 执行代码
        - GET /get_prompts: 获取 benchmark 问题
        - POST /submit: 提交代码进行评测

    Usage:
        client = SandboxFusionClient("http://localhost:8080")
        result = client.run_code("print('hello')", "python")
    """

    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        初始化客户端。

        Args:
            base_url: SandboxFusion 服务地址
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = 60

    def run_code(
        self,
        code: str,
        language: str = "python",
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        执行代码。

        Args:
            code: 要执行的代码
            language: 编程语言
            timeout: 超时时间（秒）

        Returns:
            执行结果字典
        """
        url = f"{self.base_url}/run_code"
        payload = {
            "code": code,
            "language": language
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=timeout or self.timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e),
                "run_result": {
                    "stdout": "",
                    "stderr": str(e),
                    "return_code": -1
                }
            }

    def get_prompts(
        self,
        dataset: str,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        获取 benchmark 问题。

        Args:
            dataset: 数据集名称 (mbpp, humaneval 等)
            config: 额外配置

        Returns:
            问题列表
        """
        url = f"{self.base_url}/get_prompts"
        params = {
            "dataset": dataset,
            "config": config or {}
        }

        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "prompts": []}

    def submit(
        self,
        dataset: str,
        problem_id: str,
        completion: str,
        config: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        提交代码进行评测。

        Args:
            dataset: 数据集名称
            problem_id: 问题 ID
            completion: 代码解答
            config: 额外配置

        Returns:
            评测结果
        """
        url = f"{self.base_url}/submit"
        payload = {
            "dataset": dataset,
            "id": problem_id,
            "completion": completion,
            "config": config or {}
        }

        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"accepted": False, "error": str(e)}

    def is_available(self) -> bool:
        """检查服务是否可用"""
        try:
            response = requests.get(
                f"{self.base_url}/",
                timeout=5
            )
            return response.status_code == 200
        except:
            return False


class TimeoutException(Exception):
    """代码执行超时异常"""
    pass


@contextmanager
def capture_output():
    """捕获标准输出和标准错误"""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    try:
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr


def timeout_handler(signum, frame):
    """超时信号处理"""
    raise TimeoutException("Code execution timed out")


class CodeExecuteTool(PydanticTool):
    """
    代码执行工具。

    支持两种执行模式：
    1. local: 本地沙箱执行（默认）
    2. sandbox_fusion: 使用 SandboxFusion API

    Usage:
        # 本地模式
        tool = CodeExecuteTool()
        result = tool(code="print(2 + 2)")

        # SandboxFusion 模式
        tool = CodeExecuteTool(config={
            "mode": "sandbox_fusion",
            "sandbox_url": "http://localhost:8080"
        })
        result = tool(code="print(2 + 2)")
    """

    name = "code_execute"
    description = "在安全沙箱中执行Python代码。支持数学计算、数据处理等任务。"

    input_model = CodeExecuteInput
    output_model = CodeExecuteOutput

    # 允许的内置模块（安全考虑，本地模式使用）
    ALLOWED_MODULES = {
        'math', 'random', 'datetime', 'json', 're', 'collections',
        'itertools', 'functools', 'operator', 'string', 'decimal',
        'fractions', 'statistics', 'copy', 'heapq', 'bisect'
    }

    # 禁止的内置函数（本地模式使用）
    BLOCKED_BUILTINS = {
        'eval', 'exec', 'compile', 'open', 'input', '__import__',
        'globals', 'locals', 'vars', 'dir', 'getattr', 'setattr',
        'delattr', 'hasattr'
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        config = config or {}
        self.max_output_length = config.get('max_output_length', 10000)

        # 执行模式: local 或 sandbox_fusion
        self.mode = config.get('mode', 'local')
        self.sandbox_url = config.get('sandbox_url', 'http://localhost:8080')

        # 如果是 sandbox_fusion 模式，初始化客户端
        self._sandbox_client: Optional[SandboxFusionClient] = None
        if self.mode == 'sandbox_fusion':
            self._sandbox_client = SandboxFusionClient(self.sandbox_url)

    @property
    def sandbox_client(self) -> SandboxFusionClient:
        """懒加载 SandboxFusion 客户端"""
        if self._sandbox_client is None:
            self._sandbox_client = SandboxFusionClient(self.sandbox_url)
        return self._sandbox_client

    def _create_safe_globals(self) -> Dict[str, Any]:
        """创建安全的全局命名空间"""
        import math
        import random
        import datetime
        import json
        import re
        from collections import Counter, defaultdict, deque, OrderedDict
        from itertools import permutations, combinations, product
        from functools import reduce
        from decimal import Decimal
        from fractions import Fraction
        from statistics import mean, median, mode, stdev

        safe_builtins = {
            k: v for k, v in __builtins__.items()
            if k not in self.BLOCKED_BUILTINS
        } if isinstance(__builtins__, dict) else {
            k: getattr(__builtins__, k) for k in dir(__builtins__)
            if not k.startswith('_') and k not in self.BLOCKED_BUILTINS
        }

        return {
            '__builtins__': safe_builtins,
            'math': math,
            'random': random,
            'datetime': datetime,
            'json': json,
            're': re,
            'Counter': Counter,
            'defaultdict': defaultdict,
            'deque': deque,
            'OrderedDict': OrderedDict,
            'permutations': permutations,
            'combinations': combinations,
            'product': product,
            'reduce': reduce,
            'Decimal': Decimal,
            'Fraction': Fraction,
            'mean': mean,
            'median': median,
            'mode': mode,
            'stdev': stdev,
        }

    def _execute_with_timeout(
        self,
        code: str,
        timeout: int,
        globals_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """在超时限制内执行代码"""
        result = {
            'stdout': '',
            'stderr': '',
            'return_value': None,
            'success': False,
            'error': None
        }

        def run_code():
            nonlocal result
            try:
                with capture_output() as (stdout, stderr):
                    # 执行代码
                    exec(code, globals_dict)

                    # 获取最后一个表达式的值（如果有）
                    # 这需要更复杂的AST分析，暂时跳过

                result['stdout'] = stdout.getvalue()[:self.max_output_length]
                result['stderr'] = stderr.getvalue()[:self.max_output_length]
                result['success'] = True

            except Exception as e:
                result['stderr'] = traceback.format_exc()[:self.max_output_length]
                result['error'] = str(e)
                result['success'] = False

        # 使用线程执行（支持超时）
        thread = threading.Thread(target=run_code)
        thread.daemon = True
        thread.start()
        thread.join(timeout=timeout)

        if thread.is_alive():
            result['error'] = f"Execution timed out after {timeout} seconds"
            result['success'] = False

        return result

    def _execute(self, input_data: CodeExecuteInput) -> CodeExecuteOutput:
        """
        执行代码。

        根据配置选择执行模式：local 或 sandbox_fusion

        Args:
            input_data: 验证后的输入

        Returns:
            CodeExecuteOutput: 执行结果
        """
        if self.mode == 'sandbox_fusion':
            return self._execute_sandbox_fusion(input_data)
        else:
            return self._execute_local(input_data)

    def _execute_local(self, input_data: CodeExecuteInput) -> CodeExecuteOutput:
        """
        本地沙箱执行。

        Args:
            input_data: 验证后的输入

        Returns:
            CodeExecuteOutput: 执行结果
        """
        start_time = time.time()

        # 创建安全的执行环境
        safe_globals = self._create_safe_globals()

        # 执行代码
        result = self._execute_with_timeout(
            code=input_data.code,
            timeout=input_data.timeout,
            globals_dict=safe_globals
        )

        execution_time = time.time() - start_time

        return CodeExecuteOutput(
            stdout=result['stdout'],
            stderr=result['stderr'],
            return_value=result.get('return_value'),
            success=result['success'],
            execution_time=execution_time
        )

    def _execute_sandbox_fusion(self, input_data: CodeExecuteInput) -> CodeExecuteOutput:
        """
        使用 SandboxFusion API 执行代码。

        Args:
            input_data: 验证后的输入

        Returns:
            CodeExecuteOutput: 执行结果
        """
        start_time = time.time()

        # 调用 SandboxFusion API
        result = self.sandbox_client.run_code(
            code=input_data.code,
            language="python",
            timeout=input_data.timeout
        )

        execution_time = time.time() - start_time

        # 解析 SandboxFusion 响应
        run_result = result.get('run_result', {})
        status = result.get('status', 'error')

        return CodeExecuteOutput(
            stdout=run_result.get('stdout', '')[:self.max_output_length],
            stderr=run_result.get('stderr', '')[:self.max_output_length],
            return_value=None,
            success=status == 'success' or run_result.get('return_code', -1) == 0,
            execution_time=execution_time
        )

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "要执行的Python代码"
                },
                "timeout": {
                    "type": "integer",
                    "description": "执行超时时间（秒）",
                    "default": 30
                },
                "capture_output": {
                    "type": "boolean",
                    "description": "是否捕获输出",
                    "default": True
                }
            },
            "required": ["code"]
        }


class MathSolveTool(PydanticTool):
    """
    数学求解工具。

    专门用于数学问题求解，支持符号计算和数值计算。

    Usage:
        tool = MathSolveTool()
        result = tool(problem="计算 (3 + 5) * 2 的值")
    """

    name = "math_solve"
    description = "解决数学问题。支持算术计算、代数运算、数学推理等任务。"

    def __init__(
        self,
        code_executor: Optional[CodeExecuteTool] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        super().__init__(config)
        self._code_executor = code_executor or CodeExecuteTool()

    def _execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行数学求解"""
        problem = input_data.get("problem", "")
        show_steps = input_data.get("show_steps", True)

        # 尝试直接计算（如果是简单表达式）
        if self._is_simple_expression(problem):
            return self._evaluate_expression(problem)

        # 否则生成解题代码
        code = self._generate_solution_code(problem)

        # 执行代码
        result = self._code_executor(code=code, timeout=30)

        if result.success:
            output = result.data.get("stdout", "").strip()
            return {
                "solution": output,
                "steps": [output] if output else [],
                "final_answer": self._extract_final_answer(output)
            }
        else:
            return {
                "solution": f"Error: {result.error}",
                "steps": [],
                "final_answer": "Error"
            }

    def _is_simple_expression(self, problem: str) -> bool:
        """判断是否是简单数学表达式"""
        import re
        # 匹配简单的数学表达式：数字、运算符、括号
        pattern = r'^[\d\s\+\-\*\/\(\)\.\^]+$'
        return bool(re.match(pattern, problem.replace('**', '^')))

    def _evaluate_expression(self, expr: str) -> Dict[str, Any]:
        """计算简单表达式"""
        import re
        # 将 ^ 替换为 **
        expr = expr.replace('^', '**')

        try:
            # 安全地计算表达式
            result = eval(expr, {"__builtins__": {}}, {})
            return {
                "solution": f"{expr} = {result}",
                "steps": [f"Calculate: {expr}", f"Result: {result}"],
                "final_answer": str(result)
            }
        except Exception as e:
            return {
                "solution": f"Cannot evaluate: {e}",
                "steps": [],
                "final_answer": "Error"
            }

    def _generate_solution_code(self, problem: str) -> str:
        """生成解题代码（简化版）"""
        # 这里可以接入 LLM 来生成代码
        # 目前只是一个占位实现
        return f"""
# Problem: {problem}
# This is a placeholder - integrate with LLM for actual code generation
print("Solution for: {problem}")
print("Please integrate with LLM for actual math solving")
"""

    def _extract_final_answer(self, output: str) -> str:
        """从输出中提取最终答案"""
        lines = output.strip().split('\n')
        if lines:
            return lines[-1]
        return output

    def get_parameters_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "problem": {
                    "type": "string",
                    "description": "数学问题描述"
                },
                "method": {
                    "type": "string",
                    "description": "求解方法",
                    "enum": ["symbolic", "numerical", "step_by_step"],
                    "default": "step_by_step"
                },
                "show_steps": {
                    "type": "boolean",
                    "description": "是否显示步骤",
                    "default": True
                }
            },
            "required": ["problem"]
        }


def create_code_execute_tool(
    config: Optional[Dict[str, Any]] = None
) -> CodeExecuteTool:
    """工厂函数：创建代码执行工具"""
    return CodeExecuteTool(config=config)


def create_math_solve_tool(
    config: Optional[Dict[str, Any]] = None
) -> MathSolveTool:
    """工厂函数：创建数学求解工具"""
    return MathSolveTool(config=config)
