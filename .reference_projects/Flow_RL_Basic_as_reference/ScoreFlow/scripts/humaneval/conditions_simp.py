"""
Simplified conditions for humaneval benchmark
System prompts removed and operator descriptions simplified
Based on research showing improved diversity with this approach
"""

TASK_PROMPT = '''
### 1. Problem Domain Overview
The target domain is the **HumanEval benchmark**. These problems test the ability to generate correct Python functions from detailed docstrings and function signatures.

**Core Characteristics:**
- **Input:** Function signature with comprehensive docstring describing the task, including examples
- **Required Skills:** Understanding docstring specifications, algorithm design, Python syntax, edge case handling
- **Answer Type:** Complete executable Python function implementation
- **Validation:** Must pass test cases wrapped in a `check(candidate)` function

**Common Problem Types:**
- **String Manipulation:** Pattern matching, parsing, transformation, validation
- **Mathematical Operations:** Number theory, arithmetic sequences, special calculations
- **List/Array Processing:** Sorting, filtering, searching, transformation algorithms
- **Logic Problems:** Conditional logic, state machines, decision trees
- **Data Structure Manipulation:** Working with nested structures, trees, custom sequences
- **Algorithm Implementation:** Classic algorithms, optimizations, recursive solutions

**Critical Challenges:**
- **Docstring Interpretation:** Must carefully parse examples and edge cases from docstring
- **Type Inference:** Function signature may not specify types explicitly
- **Edge Cases:** Examples in docstring often hint at special cases to handle
- **Performance Considerations:** Some problems have implicit efficiency requirements
- **Return Type Consistency:** Must match exact format expected by tests (e.g., float vs int)
- **Recursive Definitions:** Some problems define recursive relationships that need careful implementation

**Key Success Factors:**
- Carefully analyzing ALL examples in the docstring
- Understanding the mathematical or logical pattern from examples
- Implementing exactly what the docstring specifies (not over-engineering)
- Matching the exact function signature provided
- Handling edge cases mentioned or implied in examples
- Ensuring correct return types (especially float vs int distinctions)

**Common Pitfalls:**
- Misunderstanding the problem from incomplete reading of docstring
- Missing edge cases that are shown in examples but not explicitly stated
- Type errors (returning int when float is expected or vice versa)
- Off-by-one errors in sequences or ranges
- Not handling the base cases in recursive problems correctly
- Over-complicating simple problems

**HumanEval-Specific Considerations:**
- **Docstring is King:** The docstring contains ALL the specification - read it completely
- **Examples are Test Cases:** The examples in docstring often become the test cases
- **Function Signature Given:** The exact function name and parameters are provided
- **Check Function Format:** Tests are wrapped in `check(candidate)` where candidate is your function

**CRITICAL Workflow Design Considerations for HumanEval:**

### ⚠️ Understanding Operator Return Types (MUST READ!)
**ALL operators (Generate, Revise, Summarize, Ensemble) ALWAYS return STRINGS, never structured data!**

✅ **RECOMMENDED HumanEval Workflow Pattern:**
```python
async def run_workflow(self):
    import asyncio
    
    # Step 1: Extract function name (it's given in the prompt)
    func_name = await self.generate(
        instruction="Extract ONLY the function name from the def statement. Return just the name, nothing else.",
        context=""
    )
    
    # Step 2: Analyze the docstring examples
    analysis = await self.generate(
        instruction="""
        Analyze the docstring and examples carefully:
        1. What pattern do the examples show?
        2. What are the edge cases?
        3. What is the expected return type?
        Return a brief analysis in 2-3 sentences.
        """,
        context=""
    )
    
    # Step 3: Generate solution with comprehensive instructions
    solution = await self.generate(
        instruction=f"""
        Implement the function '{func_name}' based on the docstring specification.
        Analysis: {analysis}
        
        Requirements:
        1. Follow the EXACT function signature provided
        2. Implement the logic that satisfies ALL examples in the docstring
        3. Handle edge cases shown in examples
        4. Return the correct type (int, float, list, etc.) as shown in examples
        5. Include any necessary imports at the top
        6. Return ONLY the Python code, no explanations
        """,
        context=""
    )
    
    return solution
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
