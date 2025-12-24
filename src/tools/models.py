"""
Pydantic Models for Tool Inputs and Outputs

定义各工具的输入输出数据模型，替代 MetaGPT 的 operator_an.py。
"""

from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


# =============================================================================
# Generate Tool Models
# =============================================================================

class GenerateInput(BaseModel):
    """生成工具输入"""
    instruction: str = Field(..., description="生成任务的指令")
    context: Optional[str] = Field(None, description="可选的上下文信息")
    model: str = Field("qwen-turbo", description="使用的模型名称")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="采样温度")
    max_tokens: int = Field(2048, ge=1, le=32768, description="最大生成token数")


class GenerateOutput(BaseModel):
    """生成工具输出"""
    response: str = Field(..., description="生成的文本内容")
    model: str = Field(..., description="实际使用的模型")
    usage: Dict[str, int] = Field(default_factory=dict, description="Token使用统计")


# =============================================================================
# Code Execute Tool Models
# =============================================================================

class CodeExecuteInput(BaseModel):
    """代码执行工具输入"""
    code: str = Field(..., description="要执行的Python代码")
    timeout: int = Field(30, ge=1, le=300, description="执行超时时间（秒）")
    capture_output: bool = Field(True, description="是否捕获输出")


class CodeExecuteOutput(BaseModel):
    """代码执行工具输出"""
    stdout: str = Field("", description="标准输出")
    stderr: str = Field("", description="标准错误")
    return_value: Optional[str] = Field(None, description="返回值")
    success: bool = Field(..., description="执行是否成功")
    execution_time: float = Field(..., description="执行耗时（秒）")


# =============================================================================
# Search Tool Models
# =============================================================================

class SearchResult(BaseModel):
    """单个搜索结果"""
    title: str = Field(..., description="结果标题")
    content: str = Field(..., description="结果内容")
    url: Optional[str] = Field(None, description="来源URL")
    relevance_score: float = Field(0.0, ge=0.0, le=1.0, description="相关性分数")


class SearchInput(BaseModel):
    """搜索工具输入"""
    query: str = Field(..., description="搜索查询")
    search_type: str = Field("web", description="搜索类型")
    max_results: int = Field(5, ge=1, le=20, description="最大返回结果数")


class SearchOutput(BaseModel):
    """搜索工具输出"""
    results: List[SearchResult] = Field(default_factory=list, description="搜索结果列表")
    total_found: int = Field(0, description="找到的总结果数")


# =============================================================================
# Answer Tool Models
# =============================================================================

class AnswerInput(BaseModel):
    """答案生成工具输入"""
    question: str = Field(..., description="原始问题")
    context: str = Field(..., description="相关上下文信息")
    reasoning: Optional[str] = Field(None, description="推理过程")
    format: str = Field("text", description="答案格式")


class AnswerOutput(BaseModel):
    """答案生成工具输出"""
    answer: str = Field(..., description="最终答案")
    confidence: float = Field(0.5, ge=0.0, le=1.0, description="置信度")
    explanation: Optional[str] = Field(None, description="答案解释")


# =============================================================================
# Math Solve Tool Models
# =============================================================================

class MathSolveInput(BaseModel):
    """数学求解工具输入"""
    problem: str = Field(..., description="数学问题描述")
    method: str = Field("step_by_step", description="求解方法")
    show_steps: bool = Field(True, description="是否显示步骤")


class MathSolveOutput(BaseModel):
    """数学求解工具输出"""
    solution: str = Field(..., description="完整解答")
    steps: List[str] = Field(default_factory=list, description="解题步骤")
    final_answer: str = Field(..., description="最终数值答案")


# =============================================================================
# Code Generate Tool Models
# =============================================================================

class CodeGenerateInput(BaseModel):
    """代码生成工具输入"""
    task_description: str = Field(..., description="代码任务描述")
    language: str = Field("python", description="编程语言")
    include_tests: bool = Field(False, description="是否包含测试")
    style: str = Field("concise", description="代码风格")


class CodeGenerateOutput(BaseModel):
    """代码生成工具输出"""
    code: str = Field(..., description="生成的代码")
    explanation: Optional[str] = Field(None, description="代码说明")
    tests: Optional[str] = Field(None, description="测试用例")


# =============================================================================
# Generic Models
# =============================================================================

class ToolCallRequest(BaseModel):
    """工具调用请求"""
    tool_name: str = Field(..., description="工具名称")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    request_id: Optional[str] = Field(None, description="请求ID")


class ToolCallResponse(BaseModel):
    """工具调用响应"""
    success: bool = Field(..., description="是否成功")
    tool_name: str = Field(..., description="工具名称")
    data: Optional[Any] = Field(None, description="返回数据")
    error: Optional[str] = Field(None, description="错误信息")
    execution_time: float = Field(0.0, description="执行耗时")
    request_id: Optional[str] = Field(None, description="请求ID")


# =============================================================================
# Workflow Models (Single-turn)
# =============================================================================

class WorkflowStep(BaseModel):
    """工作流步骤"""
    step_id: int = Field(..., description="步骤ID")
    tool_name: str = Field(..., description="使用的工具")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="工具参数")
    depends_on: List[int] = Field(default_factory=list, description="依赖的步骤ID")


class WorkflowPlan(BaseModel):
    """工作流计划（Single-turn输出）"""
    task: str = Field(..., description="任务描述")
    steps: List[WorkflowStep] = Field(default_factory=list, description="执行步骤")
    reasoning: Optional[str] = Field(None, description="规划推理")


class WorkflowResult(BaseModel):
    """工作流执行结果"""
    success: bool = Field(..., description="是否成功")
    final_answer: Optional[str] = Field(None, description="最终答案")
    steps_executed: int = Field(0, description="执行的步骤数")
    total_time: float = Field(0.0, description="总耗时")
    step_results: List[Dict[str, Any]] = Field(default_factory=list, description="各步骤结果")


# =============================================================================
# Reward Models
# =============================================================================

class RewardRequest(BaseModel):
    """Reward计算请求"""
    task_id: str = Field(..., description="任务ID")
    question: str = Field(..., description="原始问题")
    ground_truth: str = Field(..., description="标准答案")
    model_answer: str = Field(..., description="模型答案")
    benchmark: str = Field(..., description="Benchmark名称")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")


class RewardResponse(BaseModel):
    """Reward计算响应"""
    success: bool = Field(..., description="是否成功")
    score: float = Field(..., description="总分")
    breakdown: Dict[str, Optional[float]] = Field(
        default_factory=lambda: {
            "outcome": None,
            "efficiency": None,
            "preference": None
        },
        description="分维度得分"
    )
    details: Optional[str] = Field(None, description="评分详情")
