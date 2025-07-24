"""
InternBootcamp操作符的Pydantic模型定义
用于MetaGPT ActionNode的结构化输出
"""
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field


# Standard operators from GSM8K pattern
class GenerateOp(BaseModel):
    response: str = Field(default="", description="Your solution for this problem")


class CodeGenerateOp(BaseModel):
    code: str = Field(default="", description="Your complete code solution for this problem")


class ScEnsembleOp(BaseModel):
    thought: str = Field(default="", description="The thought in the process of ensemble.") 
    solution_letter: str = Field(default="", description="The letter of most consistent solution.")
    

class ReviewOp(BaseModel):
    thought: str = Field(default="", description="The thought in the process of review.")
    revised_solution: str = Field(default="", description="The revised solution.")


class ReflectOp(BaseModel):
    thought: str = Field(default="", description="My thought process for reflecting on the provided solution. I will analyze its strengths and weaknesses.")
    reflection_text: str = Field(default="", description="A critical reflection on the solution, highlighting potential errors, unstated assumptions, or alternative perspectives.")


class FlexibleCustomOp(BaseModel):
    thought: str = Field(default="", description="My reasoning process following the specified pattern and steps.")
    solution: str = Field(default="", description="The solution derived from applying the custom reasoning pattern.")
    needs_iteration: bool = Field(default=False, description="Whether additional iterations are needed (for iterative patterns).")
    intermediate_results: str = Field(default="", description="Intermediate results or insights from this reasoning step.")


class TaskAnalyzerAN(BaseModel):
    """任务分析操作符的输入输出模型"""
    
    class Config:
        arbitrary_types_allowed = True


class TaskAnalysisOutput(BaseModel):
    """任务分析的输出"""
    task_type: str = Field(..., description="识别的任务类型(logic_puzzle/math_puzzle/algorithm_problem/graph_theory/unknown)")
    problem_description: str = Field(..., description="问题的简要描述")
    constraints: List[str] = Field(..., description="问题的约束条件列表")
    requirements: List[str] = Field(..., description="输出格式和其他要求")
    key_elements: Dict[str, Any] = Field(default_factory=dict, description="问题的关键元素(如网格大小、数字范围等)")


class StrategyPlannerAN(BaseModel):
    """策略规划操作符的输入输出模型"""
    
    class Config:
        arbitrary_types_allowed = True


class StrategyPlanOutput(BaseModel):
    """策略规划的输出"""
    approach: str = Field(..., description="解题的总体方法")
    steps: List[str] = Field(..., description="具体的解题步骤")
    algorithms: List[str] = Field(default_factory=list, description="需要使用的算法或技术")
    considerations: List[str] = Field(default_factory=list, description="需要特别注意的事项")


class ProblemSolverAN(BaseModel):
    """问题求解操作符的输入输出模型"""
    
    class Config:
        arbitrary_types_allowed = True


class ProblemSolutionOutput(BaseModel):
    """问题求解的输出"""
    solution: Union[str, List, Dict] = Field(..., description="问题的解决方案")
    reasoning: str = Field(..., description="解题推理过程")
    intermediate_steps: List[Dict[str, Any]] = Field(default_factory=list, description="中间计算步骤")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="解决方案的置信度")


class FormatExtractorAN(BaseModel):
    """格式提取操作符的输入输出模型"""
    
    class Config:
        arbitrary_types_allowed = True


class FormattedAnswerOutput(BaseModel):
    """格式化答案的输出"""
    answer: str = Field(..., description="按要求格式化的最终答案")
    format_type: str = Field(..., description="答案的格式类型(如matrix/list/dict/number等)")
    raw_content: str = Field(..., description="答案的原始内容(在[answer]标签内)")


class ValidationAN(BaseModel):
    """验证操作符的输入输出模型"""
    
    class Config:
        arbitrary_types_allowed = True


class ValidationOutput(BaseModel):
    """验证的输出"""
    is_valid: bool = Field(..., description="解决方案是否有效")
    errors: List[str] = Field(default_factory=list, description="发现的错误列表")
    warnings: List[str] = Field(default_factory=list, description="警告信息列表")
    validation_details: Dict[str, Any] = Field(default_factory=dict, description="详细的验证信息")