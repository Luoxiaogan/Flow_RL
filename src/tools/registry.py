"""
Tool Registry for New_Flow_RL

工具注册表，管理所有可用工具的注册、发现和调用。
借鉴 ToolOrchestra 的工具管理模式。
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Callable

from src.tools.base import BaseTool, FunctionTool, ToolResult
from src.core.logger import get_logger

logger = get_logger(__name__)


class ToolRegistry:
    """
    工具注册表。

    管理所有可用工具的注册、发现和调用。

    Usage:
        registry = ToolRegistry()

        # 注册工具
        registry.register(GenerateTool())

        # 或使用装饰器
        @registry.register_class
        class SearchTool(BaseTool):
            ...

        # 调用工具
        result = registry.call("generate", instruction="Hello")

        # 获取所有工具的 Schema
        schemas = registry.get_all_schemas()
    """

    _instance: Optional["ToolRegistry"] = None

    def __new__(cls):
        """单例模式"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._tools: Dict[str, BaseTool] = {}
        self._tool_schemas: Dict[str, Dict[str, Any]] = {}
        self._initialized = True
        logger.debug("ToolRegistry initialized")

    def register(self, tool: BaseTool) -> "ToolRegistry":
        """
        注册一个工具实例。

        Args:
            tool: 工具实例

        Returns:
            self（支持链式调用）
        """
        if tool.name in self._tools:
            logger.warning(f"Tool '{tool.name}' already registered, overwriting")

        self._tools[tool.name] = tool
        self._tool_schemas[tool.name] = tool.get_schema()
        logger.info(f"Registered tool: {tool.name}")
        return self

    def register_class(self, tool_class: Type[BaseTool]) -> Type[BaseTool]:
        """
        类装饰器，注册工具类。

        Usage:
            @registry.register_class
            class MyTool(BaseTool):
                ...
        """
        tool_instance = tool_class()
        self.register(tool_instance)
        return tool_class

    def register_function(
        self,
        name: str,
        description: str
    ) -> Callable[[Callable], FunctionTool]:
        """
        函数装饰器，注册函数为工具。

        Usage:
            @registry.register_function("search", "搜索信息")
            def search(query: str) -> dict:
                ...
        """
        def decorator(func: Callable) -> FunctionTool:
            tool = FunctionTool(func=func, name=name, description=description)
            self.register(tool)
            return tool
        return decorator

    def unregister(self, name: str) -> bool:
        """
        注销工具。

        Args:
            name: 工具名称

        Returns:
            是否成功注销
        """
        if name in self._tools:
            del self._tools[name]
            del self._tool_schemas[name]
            logger.info(f"Unregistered tool: {name}")
            return True
        return False

    def get(self, name: str) -> Optional[BaseTool]:
        """
        获取工具实例。

        Args:
            name: 工具名称

        Returns:
            工具实例或 None
        """
        return self._tools.get(name)

    def call(self, name: str, **kwargs) -> ToolResult:
        """
        调用工具。

        Args:
            name: 工具名称
            **kwargs: 工具参数

        Returns:
            ToolResult: 执行结果
        """
        tool = self.get(name)
        if tool is None:
            return ToolResult(
                success=False,
                error=f"Tool '{name}' not found. Available: {list(self._tools.keys())}"
            )

        try:
            return tool(**kwargs)
        except Exception as e:
            logger.error(f"Error calling tool '{name}': {e}")
            return ToolResult(success=False, error=str(e))

    def get_schema(self, name: str) -> Optional[Dict[str, Any]]:
        """
        获取工具的 Schema。

        Args:
            name: 工具名称

        Returns:
            Schema 字典或 None
        """
        return self._tool_schemas.get(name)

    def get_all_schemas(self) -> List[Dict[str, Any]]:
        """
        获取所有工具的 Schema。

        用于 LLM function calling。

        Returns:
            Schema 列表
        """
        return list(self._tool_schemas.values())

    def get_openai_tools(self) -> List[Dict[str, Any]]:
        """
        获取 OpenAI function calling 格式的工具定义。

        Returns:
            OpenAI tools 格式列表
        """
        tools = []
        for name, schema in self._tool_schemas.items():
            tools.append({
                "type": "function",
                "function": {
                    "name": schema.get("name", name),
                    "description": schema.get("description", ""),
                    "parameters": schema.get("parameters", {"type": "object", "properties": {}})
                }
            })
        return tools

    def list_tools(self) -> List[str]:
        """
        列出所有已注册的工具名称。

        Returns:
            工具名称列表
        """
        return list(self._tools.keys())

    def load_from_json(self, json_path: str) -> "ToolRegistry":
        """
        从 tools.json 加载工具定义（Schema only）。

        注意：这只加载 Schema 用于 LLM，不创建实际的工具实例。
        实际工具需要通过 register() 方法注册。

        Args:
            json_path: tools.json 文件路径

        Returns:
            self
        """
        path = Path(json_path)
        if not path.exists():
            logger.warning(f"Tools config not found: {json_path}")
            return self

        with open(path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        tools_list = config.get("tools", [])
        for tool_def in tools_list:
            name = tool_def.get("name")
            if name and name not in self._tool_schemas:
                self._tool_schemas[name] = {
                    "name": name,
                    "description": tool_def.get("description", ""),
                    "parameters": tool_def.get("parameters", {})
                }
                logger.debug(f"Loaded tool schema: {name}")

        logger.info(f"Loaded {len(tools_list)} tool schemas from {json_path}")
        return self

    def __contains__(self, name: str) -> bool:
        """支持 'tool_name' in registry 语法"""
        return name in self._tools

    def __len__(self) -> int:
        """返回已注册工具数量"""
        return len(self._tools)

    def __iter__(self):
        """迭代所有工具"""
        return iter(self._tools.values())

    def clear(self):
        """清空所有注册的工具"""
        self._tools.clear()
        self._tool_schemas.clear()
        logger.info("ToolRegistry cleared")


# 全局注册表实例
_global_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """
    获取全局工具注册表。

    Returns:
        ToolRegistry 实例
    """
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def register_tool(tool: BaseTool) -> BaseTool:
    """
    便捷函数：注册工具到全局注册表。

    Args:
        tool: 工具实例

    Returns:
        工具实例
    """
    get_registry().register(tool)
    return tool


def call_tool(name: str, **kwargs) -> ToolResult:
    """
    便捷函数：调用全局注册表中的工具。

    Args:
        name: 工具名称
        **kwargs: 工具参数

    Returns:
        ToolResult
    """
    return get_registry().call(name, **kwargs)
