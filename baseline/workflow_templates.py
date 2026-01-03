"""
Workflow templates for Chain-of-Thought (CoT) and Self-Consistency evaluation.
These workflows are designed to be executed by the reward server using MetaGPT.
最简版本 - 提示词极简，专注核心功能
"""

# Chain-of-Thought Workflow Template - 最简版
# 注意：必须用```python和```包裹
COT_WORKFLOW = '''```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)

        self.generate = operator.Generate(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        最简CoT - 一步生成答案
        """
        # 极简提示词
        instruction = "Solve the problem step by step. Return your answer in the last."
        answer = await self.generate(instruction, "")
        return answer
```'''

# Self-Consistency Workflow Template - 最简版
SELF_CONSISTENCY_WORKFLOW = '''```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)

        self.generate = operator.Generate(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        最简Self-consistency - 相同提示词运行3次，然后ensemble
        """
        solutions = []

        # 使用相同的简单提示词生成3次
        simple_instruction = "Solve this problem."

        # 第1次
        solution1 = await self.generate(simple_instruction, "")
        solutions.append(solution1)

        # 第2次
        solution2 = await self.generate(simple_instruction, "")
        solutions.append(solution2)

        # 第3次
        solution3 = await self.generate(simple_instruction, "")
        solutions.append(solution3)

        # 用ensemble选择最终答案
        ensemble_instruction = "Select the best answer."
        final_answer = await self.ensemble(ensemble_instruction, solutions)

        return final_answer
```'''

def get_workflow_template(workflow_type):
    """
    Get the workflow template by type

    Args:
        workflow_type: Either 'cot' or 'self_consistency'

    Returns:
        The workflow template string (already wrapped in ```python```)
    """
    if workflow_type.lower() == 'cot':
        return COT_WORKFLOW
    elif workflow_type.lower() in ['self_consistency', 'sc']:
        return SELF_CONSISTENCY_WORKFLOW
    else:
        raise ValueError(f"Unknown workflow type: {workflow_type}")