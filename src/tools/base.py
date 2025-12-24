"""
Tool Base Class for New_Flow_RL

替代 MetaGPT 的 ActionNode，使用普通 Python 函数 + Pydantic 实现。
借鉴 ToolOrchestra 的工具设计模式。
"""

import time
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union, Callable
from dataclasses import dataclass, field
from pydantic import BaseModel

from src.core.logger import get_logger

logger = get_logger(__name__)


@dataclass
class ToolResult:
    """
    Tool 执行结果的标准化封装。

    Attributes:
        success: 执行是否成功
        data: 返回数据（成功时）
        error: 错误信息（失败时）
        execution_time: 执行耗时（秒）
        usage: 资源使用情况（token、API调用等）
    """
    success: bool
    data: Any = None
    error: Optional[str] = None
    execution_time: float = 0.0
    usage: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "success": self.success,
            "data": self.data,
            "error": self.error,
            "execution_time": self.execution_time,
            "usage": self.usage
        }

    def __str__(self) -> str:
        if self.success:
            return f"ToolResult(success=True, data={self.data})"
        else:
            return f"ToolResult(success=False, error={self.error})"


class BaseTool(ABC):
    """
    Tool 抽象基类。

    所有工具必须继承此类并实现 execute 方法。

    Usage:
        class GenerateTool(BaseTool):
            name = "generate"
            description = "生成文本内容"

            def execute(self, instruction: str, **kwargs) -> ToolResult:
                # 实现具体逻辑
                return ToolResult(success=True, data={"response": "..."})
    """

    # 子类必须定义
    name: str = ""
    description: str = ""

    # 可选配置
    timeout: int = 60
    retry_count: int = 3
    retry_delay: float = 1.0

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        初始化工具。

        Args:
            config: 工具配置字典
        """
        self.config = config or {}
        self._validate_definition()

    def _validate_definition(self):
        """验证工具定义完整性"""
        if not self.name:
            raise ValueError(f"{self.__class__.__name__} must define 'name'")
        if not self.description:
            raise ValueError(f"{self.__class__.__name__} must define 'description'")

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        执行工具逻辑。

        Args:
            **kwargs: 工具参数

        Returns:
            ToolResult: 执行结果
        """
        pass

    def __call__(self, **kwargs) -> ToolResult:
        """
        使工具可调用。

        包装 execute 方法，添加计时、重试、错误处理。
        """
        start_time = time.time()
        last_error = None

        for attempt in range(self.retry_count):
            try:
                result = self.execute(**kwargs)
                result.execution_time = time.time() - start_time
                return result

            except Exception as e:
                last_error = e
                logger.warning(
                    f"Tool '{self.name}' failed (attempt {attempt + 1}/{self.retry_count}): {e}"
                )
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)

        # 所有重试都失败
        return ToolResult(
            success=False,
            error=str(last_error),
            execution_time=time.time() - start_time
        )

    def get_schema(self) -> Dict[str, Any]:
        """
        获取工具的 JSON Schema 定义。

        用于 LLM function calling。
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.get_parameters_schema()
        }

    def get_parameters_schema(self) -> Dict[str, Any]:
        """
        获取参数的 JSON Schema。

        子类可以重写此方法提供详细的参数定义。
        """
        return {"type": "object", "properties": {}}

    def validate_input(self, **kwargs) -> bool:
        """
        验证输入参数。

        Args:
            **kwargs: 输入参数

        Returns:
            bool: 验证是否通过
        """
        return True

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(name='{self.name}')>"


class FunctionTool(BaseTool):
    """
    基于函数的工具。

    将普通 Python 函数包装为 Tool。

    Usage:
        def my_func(query: str) -> str:
            return f"Result for: {query}"

        tool = FunctionTool(
            func=my_func,
            name="search",
            description="搜索信息"
        )
        result = tool(query="hello")
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        description: str,
        config: Optional[Dict[str, Any]] = None
    ):
        self._func = func
        self.name = name
        self.description = description
        super().__init__(config)

    def execute(self, **kwargs) -> ToolResult:
        """执行包装的函数"""
        try:
            result = self._func(**kwargs)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))


class PydanticTool(BaseTool):
    """
    基于 Pydantic 模型的工具。

    使用 Pydantic 进行输入验证和输出结构化。

    Usage:
        class GenerateInput(BaseModel):
            instruction: str
            context: Optional[str] = None

        class GenerateOutput(BaseModel):
            response: str
            model: str

        class GenerateTool(PydanticTool):
            name = "generate"
            description = "生成文本"
            input_model = GenerateInput
            output_model = GenerateOutput

            def _execute(self, input_data: GenerateInput) -> GenerateOutput:
                return GenerateOutput(response="...", model="qwen")
    """

    input_model: Optional[Type[BaseModel]] = None
    output_model: Optional[Type[BaseModel]] = None

    def execute(self, **kwargs) -> ToolResult:
        """
        执行工具，包含 Pydantic 验证。
        """
        try:
            # 验证输入
            if self.input_model:
                input_data = self.input_model(**kwargs)
            else:
                input_data = kwargs

            # 执行具体逻辑
            output = self._execute(input_data)

            # 处理输出
            if isinstance(output, BaseModel):
                data = output.model_dump()
            else:
                data = output

            return ToolResult(success=True, data=data)

        except Exception as e:
            logger.error(f"Tool '{self.name}' execution error: {e}")
            return ToolResult(success=False, error=str(e))

    @abstractmethod
    def _execute(self, input_data: Any) -> Any:
        """
        子类实现的具体执行逻辑。

        Args:
            input_data: 验证后的输入数据（Pydantic模型或字典）

        Returns:
            输出数据（Pydantic模型或任意类型）
        """
        pass

    def get_parameters_schema(self) -> Dict[str, Any]:
        """从 Pydantic 模型生成参数 Schema"""
        if self.input_model:
            return self.input_model.model_json_schema()
        return super().get_parameters_schema()


def tool(name: str, description: str):
    """
    工具装饰器。

    将普通函数快速转换为 Tool。

    Usage:
        @tool("search", "搜索信息")
        def search(query: str) -> Dict[str, Any]:
            return {"results": [...]}

        # 使用
        result = search(query="hello")
    """
    def decorator(func: Callable) -> FunctionTool:
        return FunctionTool(
            func=func,
            name=name,
            description=description
        )
    return decorator
