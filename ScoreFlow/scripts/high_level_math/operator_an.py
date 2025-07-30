from pydantic import BaseModel, Field


class GenerateOp(BaseModel):
    response: str = Field(default="", description="Your mathematical solution with rigorous reasoning")


class CodeGenerateOp(BaseModel):
    code: str = Field(default="", description="Your complete code solution for the mathematical problem")


class ScEnsembleOp(BaseModel):
    thought: str = Field(default="", description="Analysis of different solutions, comparing their mathematical validity and rigor") 
    solution_letter: str = Field(default="", description="The letter of the most mathematically sound solution")
    

class ReviewOp(BaseModel):
    thought: str = Field(default="", description="Critical mathematical review identifying logical gaps, computational errors, or proof weaknesses")
    revised_solution: str = Field(default="", description="The mathematically rigorous revised solution")


class ReflectOp(BaseModel):
    thought: str = Field(default="", description="Deep mathematical reflection on the solution's assumptions, edge cases, and alternative approaches")
    reflection_text: str = Field(default="", description="A comprehensive reflection highlighting mathematical insights, potential generalizations, or connections to other problems")


class FlexibleCustomOp(BaseModel):
    thought: str = Field(default="", description="My mathematical reasoning process following the specified pattern and steps")
    solution: str = Field(default="", description="The mathematical solution derived from applying the custom reasoning pattern")
    needs_iteration: bool = Field(default=False, description="Whether additional iterations are needed for convergence or refinement")
    intermediate_results: str = Field(default="", description="Key mathematical insights, lemmas, or intermediate theorems discovered")