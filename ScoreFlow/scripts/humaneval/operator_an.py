from pydantic import BaseModel, Field


class GenerateOp(BaseModel):
    response: str = Field(default="", description="Your solution for this problem")

class ScEnsembleOp(BaseModel):
    thought: str = Field(default="", description="The thought of the most consistent solution.")
    solution_letter: str = Field(default="", description="The letter of most consistent solution.")

class ReflectionTestOp(BaseModel):
    reflection_and_solution: str = Field(
        default="", description="Corrective solution for code execution errors or test case failures"
    )

class ReviewOp(BaseModel):
    thought: str = Field(default="", description="The thought in the process of review.")
    final_code: str = Field(default="", description="The revised code.")

class CodeFixOp(BaseModel):
    analysis: str = Field(default="", description="Analysis of the error and what needs to be fixed.")
    fixed_code: str = Field(default="", description="The corrected code that addresses the error.")


class FlexibleCustomCodeOp(BaseModel):
    thought: str = Field(default="", description="My reasoning process following the specified generation pattern and strategies.")
    code: str = Field(default="", description="The generated code solution following the custom approach.")
    needs_refinement: bool = Field(default=False, description="Whether additional refinement iterations are needed.")
    approach_notes: str = Field(default="", description="Notes on the approach taken and any insights gained.")