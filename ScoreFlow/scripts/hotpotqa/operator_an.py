from pydantic import BaseModel, Field


class GenerateOp(BaseModel):
    response: str = Field(default="", description="Your solution for this problem")

class ScEnsembleOp(BaseModel):
    thought: str = Field(default="", description="The thought of the most consistent solution.")
    solution_letter: str = Field(default="", description="The letter of most consistent solution.")

class AnswerGenerateOp(BaseModel):
    thought: str = Field(default="", description="The step by step thinking process")
    answer: str = Field(default="", description="The final answer to the question")

class ReviewOp(BaseModel):
    thought: str = Field(default="", description="The thought in the process of review.")
    revised_solution: str = Field(default="", description="The revised solution.")


class FlexibleCustomOp(BaseModel):
    thought: str = Field(default="", description="My reasoning process following the specified pattern and steps.")
    solution: str = Field(default="", description="The solution derived from applying the custom reasoning pattern.")
    needs_iteration: bool = Field(default=False, description="Whether additional iterations are needed (for iterative patterns).")
    intermediate_results: str = Field(default="", description="Intermediate results or insights from this reasoning step.")