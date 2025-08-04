from pydantic import BaseModel, Field
from typing import List, Union


class GenerateOp(BaseModel):
    response: str = Field(default="", description="Your solution for this problem")

class ScEnsembleOp(BaseModel):
    thought: str = Field(default="", description="The thought of the most consistent solution.")
    solution_letter: str = Field(default="", description="The letter of most consistent solution.")

# class AnswerGenerateOp(BaseModel):
#     thought: str = Field(default="", description="The step by step thinking process")
#     answer: str = Field(default="", description="The final answer to the question")

class ReviewOp(BaseModel):
    thought: str = Field(default="", description="The thought in the process of review.")
    revised_solution: str = Field(default="", description="The revised solution.")


class FlexibleCustomOp(BaseModel):
    thought: str = Field(default="", description="My reasoning process following the specified pattern and steps.")
    solution: str = Field(default="", description="The solution derived from applying the custom reasoning pattern.")
    needs_iteration: bool = Field(default=False, description="Whether additional iterations are needed (for iterative patterns).")
    intermediate_results: str = Field(default="", description="Intermediate results or insights from this reasoning step.")

class CountingOp(BaseModel):
    """Structured output for CountingReasoning operator."""
    thought: str = Field(
        default="", 
        description="A step-by-step explanation of what was counted and how, including any filtering criteria."
    )
    count: int = Field(
        default=0, 
        description="The final, integer result of the counting operation."
    )

class ArithmeticOp(BaseModel):
    """Structured output for ArithmeticReasoning operator."""
    thought: str = Field(
       default="",
        description="A step-by-step explanation of which numbers were extracted and what calculation was performed."
    )
    equation: str = Field(
        default="",
        description="The mathematical expression representing the calculation (e.g., '45.5 + 10.0 - 5.0')."
    )
    result: float = Field(
        default=0.0,
        description="The final numerical result of the arithmetic operation."
    )

class ComparisonOp(BaseModel):
    """Structured output for ComparisonReasoning operator."""
    thought: str = Field(
        default="",
        description="A step-by-step explanation of what entities were compared and based on what criteria (e.g., 'Compared the scores of Team A (45) and Team B (38)')."
    )
    # 使用 Union 来允许返回单个字符串或一个字符串列表
    result: Union[str, List[str]] = Field(
        default="",
        description="The result of the comparison. This could be the name of the single best item (e.g., 'Team A') or an ordered list of items (e.g., ['Player C', 'Player A', 'Player B'])."
    )

# 文件: operator_an.py

class FormatAnswerOp(BaseModel):
    """Ensures the final answer is extracted and structured correctly."""
    final_answer: str = Field(
        default="",
        description="The single, core final answer extracted from the raw workflow output."
    )