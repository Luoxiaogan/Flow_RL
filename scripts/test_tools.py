#!/usr/bin/env python3
"""
Test script for Tools module.

验证点：能调用 tool 并返回结构化结果

Usage:
    python scripts/test_tools.py
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.logger import setup_logger

logger = setup_logger("test_tools", level="DEBUG")


def test_tool_base():
    """测试 Tool 基类"""
    logger.info("=" * 50)
    logger.info("Test 1: Tool Base Classes")
    logger.info("=" * 50)

    from src.tools.base import BaseTool, FunctionTool, ToolResult, tool

    # 测试 FunctionTool
    def simple_func(text: str) -> str:
        return f"Echo: {text}"

    func_tool = FunctionTool(
        func=simple_func,
        name="echo",
        description="Echo the input"
    )

    result = func_tool(text="Hello World")
    logger.info(f"FunctionTool result: {result}")
    assert result.success, f"Expected success, got: {result}"
    assert result.data == "Echo: Hello World"

    # 测试 @tool 装饰器
    @tool("double", "Double a number")
    def double_func(n: int) -> int:
        return n * 2

    result = double_func(n=5)
    logger.info(f"@tool decorator result: {result}")
    assert result.success
    assert result.data == 10

    logger.info("Tool base classes: PASSED")
    return True


def test_registry():
    """测试工具注册表"""
    logger.info("=" * 50)
    logger.info("Test 2: Tool Registry")
    logger.info("=" * 50)

    from src.tools.registry import ToolRegistry, get_registry
    from src.tools.base import FunctionTool

    # 创建新的注册表
    registry = ToolRegistry()
    registry.clear()  # 确保干净状态

    # 注册工具
    def add_func(a: int, b: int) -> int:
        return a + b

    add_tool = FunctionTool(
        func=add_func,
        name="add",
        description="Add two numbers"
    )
    registry.register(add_tool)

    # 测试获取
    assert "add" in registry
    assert len(registry) == 1

    # 测试调用
    result = registry.call("add", a=3, b=4)
    logger.info(f"Registry call result: {result}")
    assert result.success
    assert result.data == 7

    # 测试 Schema
    schemas = registry.get_all_schemas()
    logger.info(f"Schemas: {schemas}")
    assert len(schemas) == 1

    # 测试 OpenAI tools 格式
    openai_tools = registry.get_openai_tools()
    logger.info(f"OpenAI tools format: {openai_tools}")

    logger.info("Tool registry: PASSED")
    return True


def test_code_execute():
    """测试代码执行工具"""
    logger.info("=" * 50)
    logger.info("Test 3: Code Execute Tool")
    logger.info("=" * 50)

    from src.tools.code_execute import CodeExecuteTool

    tool = CodeExecuteTool()

    # 测试简单计算
    result = tool(code="print(2 + 3)")
    logger.info(f"Simple calc result: {result}")
    assert result.success
    assert "5" in result.data.get("stdout", "")

    # 测试数学库（模块已预加载，无需import）
    result = tool(code="print(math.sqrt(16))")
    logger.info(f"Math lib result: {result}")
    assert result.success
    assert "4" in result.data.get("stdout", "")

    # 测试错误处理
    result = tool(code="1/0")
    logger.info(f"Error handling result: {result}")
    assert not result.data.get("success", True)  # 应该失败

    # 测试超时
    result = tool(code="import time\ntime.sleep(100)", timeout=1)
    logger.info(f"Timeout result: {result}")
    assert not result.data.get("success", True)  # 应该超时

    logger.info("Code execute tool: PASSED")
    return True


def test_math_solve():
    """测试数学求解工具"""
    logger.info("=" * 50)
    logger.info("Test 4: Math Solve Tool")
    logger.info("=" * 50)

    from src.tools.code_execute import MathSolveTool

    tool = MathSolveTool()

    # 测试简单表达式
    result = tool(problem="3 + 5 * 2")
    logger.info(f"Simple expression result: {result}")
    assert result.success
    assert "13" in result.data.get("final_answer", "")

    # 测试括号
    result = tool(problem="(3 + 5) * 2")
    logger.info(f"Parentheses result: {result}")
    assert result.success
    assert "16" in result.data.get("final_answer", "")

    logger.info("Math solve tool: PASSED")
    return True


def test_pydantic_models():
    """测试 Pydantic 模型"""
    logger.info("=" * 50)
    logger.info("Test 5: Pydantic Models")
    logger.info("=" * 50)

    from src.tools.models import (
        GenerateInput, GenerateOutput,
        CodeExecuteInput, CodeExecuteOutput,
        ToolCallRequest, ToolCallResponse
    )

    # 测试 GenerateInput
    gen_input = GenerateInput(
        instruction="写一首诗",
        context="关于春天",
        model="qwen-turbo",
        temperature=0.7
    )
    logger.info(f"GenerateInput: {gen_input}")
    assert gen_input.instruction == "写一首诗"

    # 测试 CodeExecuteInput 默认值
    code_input = CodeExecuteInput(code="print(1)")
    assert code_input.timeout == 30
    assert code_input.capture_output is True

    # 测试 ToolCallRequest/Response
    request = ToolCallRequest(
        tool_name="generate",
        parameters={"instruction": "test"}
    )
    logger.info(f"ToolCallRequest: {request}")

    response = ToolCallResponse(
        success=True,
        tool_name="generate",
        data={"response": "test output"},
        execution_time=0.5
    )
    logger.info(f"ToolCallResponse: {response}")

    logger.info("Pydantic models: PASSED")
    return True


def test_setup_default_tools():
    """测试默认工具设置"""
    logger.info("=" * 50)
    logger.info("Test 6: Setup Default Tools")
    logger.info("=" * 50)

    from src.tools import setup_default_tools, ToolRegistry

    registry = ToolRegistry()
    registry.clear()

    setup_default_tools(registry)

    tools = registry.list_tools()
    logger.info(f"Registered tools: {tools}")

    # 应该有这些工具
    expected = ["generate", "answer", "code_execute", "math_solve"]
    for tool_name in expected:
        assert tool_name in tools, f"Missing tool: {tool_name}"

    logger.info("Setup default tools: PASSED")
    return True


def main():
    """运行所有测试"""
    logger.info("Starting Tools Module Tests")
    logger.info("=" * 60)

    results = {}

    # 运行测试
    try:
        results["tool_base"] = test_tool_base()
    except Exception as e:
        logger.error(f"test_tool_base failed: {e}")
        results["tool_base"] = False

    try:
        results["registry"] = test_registry()
    except Exception as e:
        logger.error(f"test_registry failed: {e}")
        results["registry"] = False

    try:
        results["code_execute"] = test_code_execute()
    except Exception as e:
        logger.error(f"test_code_execute failed: {e}")
        results["code_execute"] = False

    try:
        results["math_solve"] = test_math_solve()
    except Exception as e:
        logger.error(f"test_math_solve failed: {e}")
        results["math_solve"] = False

    try:
        results["pydantic_models"] = test_pydantic_models()
    except Exception as e:
        logger.error(f"test_pydantic_models failed: {e}")
        results["pydantic_models"] = False

    try:
        results["setup_default_tools"] = test_setup_default_tools()
    except Exception as e:
        logger.error(f"test_setup_default_tools failed: {e}")
        results["setup_default_tools"] = False

    # 汇总结果
    logger.info("=" * 60)
    logger.info("Test Results Summary")
    logger.info("=" * 60)

    passed = 0
    failed = 0
    for test_name, result in results.items():
        status = "PASSED" if result else "FAILED"
        logger.info(f"  {test_name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1

    logger.info("-" * 40)
    logger.info(f"Total: {passed} passed, {failed} failed")

    if failed > 0:
        logger.warning("Some tests failed.")
        return 1
    else:
        logger.info("All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
