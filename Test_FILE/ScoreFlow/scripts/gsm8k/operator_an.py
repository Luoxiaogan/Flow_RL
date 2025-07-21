from pydantic import BaseModel, Field


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