
"""
InternBootcamp工作流生成条件和模板
"""

# 元提示列表 - 用于生成多样化的工作流
META_PROMPTS = [
    ""
]

# 系统提示 - 用于SFT训练
SYSTEM_PROMPT = """
Your fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:
1. A high-level description of the problem domain
2. A strictly defined set of callable software "Operators" that serve as your only building blocks
3. An illustrative example instance, provided solely to help you understand the abstract reasoning pattern

**Your response MUST strictly adhere to a two-part format: first, a `<think>...</think>` block for your reasoning, followed by a `<code>...</code>` block for the Python solution.**

Your generated Python workflow must be robust enough to work for any problem instance within the described domain.
"""


# 工作流生成的开始提示 - 使用预定义操作符
START_PROMPT = '''
### Problem Domain Overview
{prompt_text}

Create a workflow class called `InternBootcampWorkflow` that:
1. Uses the predefined operators (Custom, Review, ScEnsemble...) to analyze and solve the problem
2. Combines multiple operators for better results
3. Handles different problem types flexibly
4. Ensures correct output format
5. Can be executed with MetaGPT

### Available Operators & Building Blocks

All operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.

### Core Operators

**1. Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`

**2. Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`

**3. Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`

**4. Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`


### Your Task: Complete the `run_workflow` Method

**Base Template:**
<think>
[Your step-by-step reasoning about the workflow strategy, why you chose specific operators, and how you'll use instructions effectively]
</think>
<code>
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Implement the core problem-solving logic here.
        Remember: 
        - Use detailed, comprehensive instructions
        - Dynamic instruction construction is powerful
        - All operators expect (instruction: str, context: str) except Ensemble which takes contexts: List[str]
        """
        import asyncio
        # --- YOUR WORKFLOW LOGIC HERE ---
</code>
### Illustrative Example(s)

The following examples help you understand the problem type. Create a workflow for the *class* of problems, not just these instances.

'''


# 工作流生成的结束提示
END_PROMPT = '''
'''

# Python执行的开始模板 - 预定义操作符
PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

PYTHON_END = '''

    async def __call__(self):
        """
        This is the main entry point that executes the workflow.
        It returns the raw result from the workflow execution.
        """
        TIMEOUT = {time}

        try:
            # Execute the LLM-generated workflow to get the raw result.
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            
            # Return the raw result directly - answer extraction is now handled in handler
            return raw_result

        except asyncio.TimeoutError:
            # Handle workflow execution timeout gracefully.
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            # Handle other potential errors during workflow execution.
            import traceback
            # 错误详情在这里被定义和使用，不暴露给外部.format()
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred during workflow execution. Details: {{escaped_error_details}}"
'''

# 选择使用哪种工作流类型
def get_workflow_prompts():
    """
    获取工作流生成的提示词
    
    Returns:
        dict: 包含START_PROMPT和PYTHON_START的字典
    """
    return {
        "START_PROMPT": START_PROMPT,
        "PYTHON_START": PYTHON_START
    }

