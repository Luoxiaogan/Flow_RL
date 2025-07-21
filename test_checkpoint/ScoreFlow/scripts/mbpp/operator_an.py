# ScoreFlow/scripts/mbpp/operator_an.py

from pydantic import BaseModel, Field
from typing import Optional, List

# --- 这是 CodeRunner 的返回类型定义，它不是给LLM用的，而是给Python内部用的 ---
class CodeRunnerResult(BaseModel):
    """
    一个结构化的数据类，用于封装 CodeRunner Operator 的执行结果。
    这使得工作流可以轻松地检查执行状态并获取错误信息。
    """
    is_correct: bool = Field(description="如果所有测试用例都通过，则为 True，否则为 False。")
    error_message: Optional[str] = Field(default=None, description="如果测试失败或发生执行异常，则包含详细的错误信息或堆栈跟踪。")


# --- 以下是给LLM用的Pydantic模型，用于解析LLM的输出 ---

class CodeGenerateOp(BaseModel):
    """
    用于代码生成操作的输出模型。
    对应 CustomCodeGenerate Operator。
    """
    code: str = Field(
        default="", 
        description="The complete, executable Python code solution for the problem. It should contain only the function definition and necessary imports, without any extra text, examples, or test cases."
    )

class ScEnsembleOp(BaseModel):
    """
    用于集成多个代码解决方案的输出模型。
    """
    thought: str = Field(
        default="", 
        description="A detailed thought process explaining why a particular solution was chosen as the best one, considering factors like correctness, efficiency, and clarity."
    )
    solution_letter: str = Field(
        default="", 
        description="The single letter ID (A, B, C, etc.) of the most consistent and accurate code solution."
    )

class CodeFixOp(BaseModel):
    """
    用于代码修复操作的输出模型。
    当 CodeRunner 失败时，LLM 会被要求反思并生成修复后的代码。
    """
    thought: str = Field(
        default="",
        description="A step-by-step analysis of why the previous code failed the test cases. This includes identifying logical errors, edge case handling issues, or misunderstandings of the problem description."
    )
    fixed_code: str = Field(
        default="",
        description="The complete, revised Python code that addresses the identified failures. It should be a fully functional replacement for the original code, containing only the function definition."
    )