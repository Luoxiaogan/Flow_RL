# Task description
TASK_PROMPT = '''### 1. Problem Domain Overview
The target domain is **HumanEval+ (Enhanced HumanEval)**.

**Core Characteristics:**
- **Input:** Function signatures with detailed docstrings and examples
- **Output:** Complete Python function implementations
- **Skills:** Algorithm design, edge case handling, type hints, complex logic
- **Enhanced Testing:** Significantly more test cases than original HumanEval for robustness
'''

# System prompt
SYSTEM_PROMPT = '''Your fundamental purpose is to act as an expert Python programmer.
You implement functions that precisely match specifications and handle all edge cases.

Your response MUST follow this format:
1. A `<think>...</think>` block with your reasoning
2. A Python code block with the complete implementation
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
   - Generate initial function implementation from specification
   
**2. Revise:** `await self.revise(instruction: str, context: str) -> str`
   - Refine and debug existing implementation

**3. Summarize:** `await self.summarize(instruction: str, context: str) -> str`
   - Extract key requirements or simplify complex specifications

**4. Ensemble:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
   - Combine multiple implementation approaches

### 3. Your Task

Create a workflow to solve HumanEval+ problems using the operators above.

**Key Strategies:**
1. Carefully analyze the function signature and docstring
2. Understand all examples provided
3. Implement a solution that handles edge cases
4. Ensure type hints are correctly used
5. Consider performance for large inputs

<think>
For HumanEval+ problems, I should:
1. Use Generate to create an initial implementation following the exact signature
2. Pay attention to the examples in the docstring
3. Use Revise to ensure edge cases are handled
4. Make sure the function name matches exactly
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
        
        # Step 1: Analyze requirements
        requirements = await self.summarize(
            instruction="Extract the key requirements: function name, parameters, return type, and critical logic from the docstring examples."
        )
        
        # Step 2: Generate initial implementation
        initial_code = await self.generate(
            instruction="Implement the function exactly as specified. Pay careful attention to the function signature, type hints, and examples in the docstring.",
            context=requirements
        )
        
        # Step 3: Refine for edge cases
        refined_code = await self.revise(
            instruction="Review the implementation and ensure it handles all edge cases mentioned in the docstring. Verify the function name and signature match exactly.",
            context=initial_code
        )
        
        return f"Final Answer:\\n```python\\n{refined_code}\\n```"
```
'''