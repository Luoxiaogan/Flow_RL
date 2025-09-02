"""
Simplified conditions for mbpp benchmark
System prompts removed and operator descriptions simplified
Based on research showing improved diversity with this approach
"""

TASK_PROMPT = '''
### 1. Problem Domain Overview
The target domain is the **MBPP benchmark** (Mostly Basic Python Problems). These problems test the ability to generate correct Python functions from natural language descriptions.

**Core Characteristics:**
- **Input:** Natural language description of a programming task
- **Required Skills:** Understanding task requirements, algorithm design, Python syntax, edge case handling
- **Answer Type:** Executable Python function code
- **Validation:** Must pass provided test cases (assert statements)

**Common Problem Types:**
- **Array/List Operations:** Finding elements, computing sums, manipulating sequences
- **Mathematical Computations:** Prime numbers, GCD/LCM, combinatorics, number theory
- **String Manipulation:** Pattern matching, parsing, formatting, validation
- **Data Structure Operations:** Dictionary/set operations, tree/graph algorithms
- **Algorithm Implementation:** Sorting variants, search algorithms, dynamic programming

**Critical Challenges:**
- **Specification Ambiguity:** Natural language may be imprecise or allow multiple interpretations
- **Edge Cases:** Must handle empty inputs, boundary values, special cases
- **Efficiency Requirements:** Some problems have implicit performance expectations
- **Python Idioms:** Solutions should be Pythonic and follow best practices
- **Function Signature:** Must infer correct parameter names and return types
- **Import Dependencies:** Must include necessary import statements for standard library modules

**Key Success Factors:**
- Understanding the exact requirements from the description
- Identifying all edge cases and constraints
- Writing clean, efficient, and correct Python code
- Ensuring the function signature matches test expectations
- Handling type conversions and input validation appropriately
- **Including all necessary import statements** (e.g., `import math`, `import re`, `from collections import Counter`)

**Common Pitfalls:**
- Off-by-one errors in indexing or range operations
- Incorrect handling of empty or None inputs
- Type mismatches (returning string instead of int, etc.)
- Missing base cases in recursive solutions
- Incorrect variable scoping or mutation of inputs
- **Forgetting to import required modules** (e.g., using `math.sqrt()` without `import math`)

**CRITICAL Workflow Design Considerations for MBPP:**

### ⚠️ Understanding Operator Return Types (MUST READ!)
**ALL operators (Generate, Revise, Summarize, Ensemble) ALWAYS return STRINGS, never structured data!**

❌ **WRONG - This will cause TypeError:**
```python
# Generate returns a string, NOT a dictionary!
result = await self.generate(instruction="Return JSON with keys 'name' and 'age'", context="")
name = result["name"]  # TypeError: string indices must be integers
```

✅ **CORRECT Option 1 - Parse JSON string:**
```python
import json  # Remember to import json at the beginning of run_workflow
result_json = await self.generate(instruction="Return JSON with keys 'name' and 'age'", context="")
result = json.loads(result_json)  # Parse string to dict
name = result["name"]  # Now this works
```

✅ **BETTER Option 2 - Use simple text (RECOMMENDED for MBPP):**
```python
# Ask for simple, directly usable text instead of JSON
func_name = await self.generate(
    instruction="Extract the function name from the test cases. Return ONLY the function name, nothing else.",
    context=""
)
# Now func_name is directly usable: "first_repeated_char"
```

### Recommended MBPP Workflow Pattern:
```python
async def run_workflow(self):
    import asyncio
    # Import any needed modules here
    
    # Step 1: Simple extraction (returns plain text)
    func_name = await self.generate(
        instruction="What is the function name in the test cases? Return ONLY the name.",
        context=""
    )
    
    # Step 2: Generate code with comprehensive instructions
    code = await self.generate(
        instruction=f"""
        Write a Python function named '{func_name}' that solves this task.
        Requirements:
        1. Include ALL necessary import statements at the top
        2. Handle edge cases (empty inputs, None, boundaries)
        3. Return ONLY the executable Python code, no explanations
        """,
        context=""
    )
    
    # Step 3: Revise if needed
    final_code = await self.revise(
        instruction="Check for missing imports and edge cases. Fix any issues. Return only the corrected code.",
        context=code
    )
    
    return final_code
```


'''

# SYSTEM_PROMPT removed - research shows training without system prompts
# but using them at inference improves both safety and diversity
SYSTEM_PROMPT = ''

PYTHON_START = '''
import asyncio
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

# Simplified START_PROMPT - reduced from ~3000 words to ~300 words
# Preserves all functional information while removing redundancy
START_PROMPT = '''
### 2. Core Operators

You have access to four fundamental operators, each pre-initialized with problem_text:
- **Generate(instruction: str, context: str = "") -> str**: Creates new content based on instructions
- **Revise(instruction: str, context: str) -> str**: Improves existing content
- **Summarize(instruction: str, context: str) -> str**: Condenses while preserving key information
- **Ensemble(instruction: str, contexts: List[str]) -> str**: Synthesizes multiple inputs

### 3. Meta-Learning Task & Implementation Guidelines

**Your Task:** Design a reusable Python workflow template that solves the entire problem CLASS, not specific instances. This is meta-learning - you're creating a system that learns patterns, not memorizing solutions.

**Key Guidelines:**
- Instructions should be comprehensive (100-500+ words when needed)
- Use f-strings for dynamic instruction construction
- Leverage asyncio.gather() for parallel operations
- Context parameter carries the actual data to process
- Never hardcode problem-specific information

**Response Format Required:**
1. A `<think>...</think>` block explaining your general solution strategy
2. A Python code block with the complete workflow implementation

**Template Structure:**
```python
class Workflow:
    def __init__(self, config, problem) -> None:
        # Pre-initialized operators - DO NOT MODIFY
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
    
    async def run_workflow(self):
        import asyncio
        # YOUR GENERIC WORKFLOW LOGIC HERE
        # Must work for ANY instance of this problem type
        pass
```
'''
