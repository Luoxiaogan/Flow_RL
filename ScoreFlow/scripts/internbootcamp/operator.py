"""
InternBootcamp操作符定义
提供通用的问题解决操作符，适用于各种任务类型
"""
from typing import Dict, Any, List, Optional, Union
from metagpt.actions import ActionNode
from metagpt.logs import logger

from .operator_an import (
    TaskAnalyzerAN, TaskAnalysisOutput,
    ProblemSolverAN, ProblemSolutionOutput,
    FormatExtractorAN, FormattedAnswerOutput,
    ValidationAN, ValidationOutput,
    StrategyPlannerAN, StrategyPlanOutput
)
from .op_prompt import (
    TASK_ANALYZER_PROMPT,
    PROBLEM_SOLVER_PROMPT,
    FORMAT_EXTRACTOR_PROMPT,
    VALIDATION_PROMPT,
    STRATEGY_PLANNER_PROMPT
)


class TaskAnalyzer:
    """分析任务类型和要求"""
    
    def __init__(self):
        self.name = "TaskAnalyzer"
        
    async def run(self, problem: str) -> TaskAnalysisOutput:
        """分析问题类型、约束和要求"""
        node = ActionNode.from_pydantic(TaskAnalyzerAN)
        response = await node.fill(context=TASK_ANALYZER_PROMPT.format(problem=problem))
        return response


class StrategyPlanner:
    """制定解题策略"""
    
    def __init__(self):
        self.name = "StrategyPlanner"
        
    async def run(self, problem: str, task_analysis: TaskAnalysisOutput) -> StrategyPlanOutput:
        """基于任务分析制定解题策略"""
        context = STRATEGY_PLANNER_PROMPT.format(
            problem=problem,
            task_type=task_analysis.task_type,
            constraints="\n".join(task_analysis.constraints),
            requirements="\n".join(task_analysis.requirements)
        )
        node = ActionNode.from_pydantic(StrategyPlannerAN)
        response = await node.fill(context=context)
        return response


class ProblemSolver:
    """执行解题逻辑"""
    
    def __init__(self):
        self.name = "ProblemSolver"
        
    async def run(self, problem: str, strategy: StrategyPlanOutput) -> ProblemSolutionOutput:
        """根据策略解决问题"""
        context = PROBLEM_SOLVER_PROMPT.format(
            problem=problem,
            approach=strategy.approach,
            steps="\n".join(f"{i+1}. {step}" for i, step in enumerate(strategy.steps))
        )
        node = ActionNode.from_pydantic(ProblemSolverAN)
        response = await node.fill(context=context)
        return response


class FormatExtractor:
    """提取并格式化答案"""
    
    def __init__(self):
        self.name = "FormatExtractor"
        
    async def run(self, problem: str, solution: ProblemSolutionOutput, 
                  requirements: List[str]) -> FormattedAnswerOutput:
        """从解决方案中提取格式化的答案"""
        context = FORMAT_EXTRACTOR_PROMPT.format(
            problem=problem,
            solution=solution.solution,
            reasoning=solution.reasoning,
            format_requirements="\n".join(requirements)
        )
        node = ActionNode.from_pydantic(FormatExtractorAN)
        response = await node.fill(context=context)
        return response


class SolutionValidator:
    """验证解决方案"""
    
    def __init__(self):
        self.name = "SolutionValidator"
        
    async def run(self, problem: str, solution: ProblemSolutionOutput,
                  formatted_answer: FormattedAnswerOutput,
                  constraints: List[str]) -> ValidationOutput:
        """验证解决方案的正确性"""
        context = VALIDATION_PROMPT.format(
            problem=problem,
            solution=solution.solution,
            answer=formatted_answer.answer,
            constraints="\n".join(constraints)
        )
        node = ActionNode.from_pydantic(ValidationAN)
        response = await node.fill(context=context)
        return response


# 便捷的操作符集合
class InternBootcampOperators:
    """InternBootcamp操作符集合"""
    
    TaskAnalyzer = TaskAnalyzer
    StrategyPlanner = StrategyPlanner
    ProblemSolver = ProblemSolver
    FormatExtractor = FormatExtractor
    SolutionValidator = SolutionValidator
    
    @classmethod
    def get_all_operators(cls) -> Dict[str, Any]:
        """获取所有操作符"""
        return {
            "TaskAnalyzer": cls.TaskAnalyzer,
            "StrategyPlanner": cls.StrategyPlanner,
            "ProblemSolver": cls.ProblemSolver,
            "FormatExtractor": cls.FormatExtractor,
            "SolutionValidator": cls.SolutionValidator
        }