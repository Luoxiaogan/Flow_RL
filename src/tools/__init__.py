"""
Tools Module for New_Flow_RL

替代 MetaGPT Operator，使用普通 Python 函数 + Pydantic 实现。
"""

from src.tools.base import (
    BaseTool,
    FunctionTool,
    PydanticTool,
    ToolResult,
    tool
)

from src.tools.registry import (
    ToolRegistry,
    get_registry,
    register_tool,
    call_tool
)

from src.tools.models import (
    # Generate
    GenerateInput,
    GenerateOutput,
    # Code Execute
    CodeExecuteInput,
    CodeExecuteOutput,
    # Search
    SearchInput,
    SearchOutput,
    SearchResult,
    # Answer
    AnswerInput,
    AnswerOutput,
    # Math
    MathSolveInput,
    MathSolveOutput,
    # Code Generate
    CodeGenerateInput,
    CodeGenerateOutput,
    # Generic
    ToolCallRequest,
    ToolCallResponse,
    # Workflow
    WorkflowStep,
    WorkflowPlan,
    WorkflowResult,
    # Reward
    RewardRequest,
    RewardResponse
)

from src.tools.generate import (
    GenerateTool,
    AnswerTool,
    create_generate_tool,
    create_answer_tool
)

from src.tools.code_execute import (
    CodeExecuteTool,
    MathSolveTool,
    SandboxFusionClient,
    create_code_execute_tool,
    create_math_solve_tool
)


def setup_default_tools(registry: ToolRegistry = None) -> ToolRegistry:
    """
    设置默认工具集。

    Args:
        registry: 工具注册表（如不提供则使用全局注册表）

    Returns:
        配置好的注册表
    """
    if registry is None:
        registry = get_registry()

    # 注册默认工具
    registry.register(GenerateTool())
    registry.register(AnswerTool())
    registry.register(CodeExecuteTool())
    registry.register(MathSolveTool())

    return registry


__all__ = [
    # Base
    'BaseTool',
    'FunctionTool',
    'PydanticTool',
    'ToolResult',
    'tool',
    # Registry
    'ToolRegistry',
    'get_registry',
    'register_tool',
    'call_tool',
    # Tools
    'GenerateTool',
    'AnswerTool',
    'CodeExecuteTool',
    'MathSolveTool',
    'SandboxFusionClient',
    # Factory functions
    'create_generate_tool',
    'create_answer_tool',
    'create_code_execute_tool',
    'create_math_solve_tool',
    'setup_default_tools',
    # Models
    'GenerateInput',
    'GenerateOutput',
    'CodeExecuteInput',
    'CodeExecuteOutput',
    'SearchInput',
    'SearchOutput',
    'SearchResult',
    'AnswerInput',
    'AnswerOutput',
    'MathSolveInput',
    'MathSolveOutput',
    'CodeGenerateInput',
    'CodeGenerateOutput',
    'ToolCallRequest',
    'ToolCallResponse',
    'WorkflowStep',
    'WorkflowPlan',
    'WorkflowResult',
    'RewardRequest',
    'RewardResponse',
]
