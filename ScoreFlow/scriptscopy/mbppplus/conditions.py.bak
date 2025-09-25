# Task description
TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is **MBPP+ (Enhanced Mostly Basic Python Problems)**.

**Core Characteristics:**
- **Input:** Programming task descriptions with test cases
- **Output:** Complete Python function implementations
- **Skills:** Algorithm design, data structures, string manipulation, mathematical operations
- **Enhanced Testing:** More comprehensive test suites than original MBPP
'''

# System prompt
SYSTEM_PROMPT = '''Your fundamental purpose is to act as an expert Python programmer.
You translate problem specifications into correct, efficient Python implementations.

Your response MUST follow this format:
1. A `<think>...</think>` block with your reasoning
2. A Python code block with the complete solution
'''

# Python code header
PYTHON_START = '''import asyncio
from typing import Literal, List, Dict, Any, Union
import ScoreFlow.scripts.common.operator as operator
from metagpt.provider.llm_provider_registry import create_llm_instance as create

'''

# Python code footer (fixed template)
PYTHON_END = '''
    async def __call__(self):
        """
        Main entry point that executes the workflow.
        """
        TIMEOUT = {time}

        try:
            raw_result = await asyncio.wait_for(self.run_workflow(), timeout=TIMEOUT)
            return raw_result

        except asyncio.TimeoutError:
            return "Final Answer: Error - Workflow execution timed out."
        except Exception as e:
            import traceback
            error_details_str = traceback.format_exc()
            escaped_error_details = error_details_str.replace("\\n", "\\\\n").replace('"', '\\"')
            return f"Final Answer: Error - An exception occurred. Details: {{escaped_error_details}}"
'''

# Operator instructions
START_PROMPT = '''### 2. Available Operators

**1. Generate:** `await self.generate(instruction: str, context: str = "") -> str`
   - Generate initial code solution based on problem description
   
**2. Revise:** `await self.revise(instruction: str, context: str) -> str`
   - Refine and improve existing code

**3. Summarize:** `await self.summarize(instruction: str, context: str) -> str`
   - Extract key information or simplify complex problems

**4. Ensemble:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
   - Combine multiple solutions or approaches

### 3. Your Task

Create a workflow to solve MBPP+ programming problems using the operators above.

**Key Strategies:**
1. Analyze the problem requirements and test cases
2. Generate a complete Python function solution
3. Ensure the code handles all edge cases
4. Consider optimizing for efficiency if needed

<think>
For MBPP+ problems, I should:
1. Use Generate to create an initial solution based on the problem description
2. Analyze test cases to understand edge cases
3. Use Revise if the solution needs refinement
4. Ensure the final code is clean and well-structured
</think>
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        
        # Step 1: Generate initial solution
        initial_solution = await self.generate(
            instruction="Generate a complete Python function that solves the given problem. Include all necessary imports and handle edge cases shown in the test cases."
        )
        
        # Step 2: Review and refine the solution
        refined_solution = await self.revise(
            instruction="Review this solution and ensure it correctly handles all test cases. Fix any issues and optimize if possible.",
            context=initial_solution
        )
        
        return f"Final Answer:\\n```python\\n{refined_solution}\\n```"
```
'''