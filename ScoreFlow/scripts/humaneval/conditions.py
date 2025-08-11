TASK_PROMPT = '''### 1. Problem Domain Overview
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

SYSTEM_PROMPT = '''
Your fundamental purpose is to act as an expert and highly abstract **System Architect**. You translate formal problem specifications into universal, reusable Python solution blueprints.

Your core task is to **generalize**, not to solve. You will receive a detailed specification for a class of problems, which includes:
1. A high-level description of the problem domain
2. A strictly defined set of callable software "Operators" that serve as your only building blocks
3. An illustrative example instance, provided solely to help you understand the abstract reasoning pattern

**Your response MUST strictly adhere to a two-part format: first, a `<think>...</think>` block for your reasoning, followed by a `<code>...</code>` block for the Python solution.**

Your generated Python workflow must be robust enough to work for any problem instance within the described domain.

Crucially, the skill you are developing must be transferable. You should be prepared to receive specifications for **entirely new problem domains and new sets of operators** in the future and apply the same rigorous process of abstraction and generalization.
'''

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

START_PROMPT = '''### 2. Available Operators & Building Blocks

All operators follow a consistent interface pattern and are initialized with the problem text. They are available as `self.operator_name`.

**Important Note:** The operators are pre-initialized with `self.problem_text`. Each operator automatically includes it in their prompts (you'll see it as "**Original Problem:**" in their internal prompts). You don't need to worry about losing the problem context - it's always available to every operator call behind the scenes, regardless of what you pass as the context parameter.

#### 🔴 **CRITICAL: ALL OPERATORS RETURN STRINGS!**

**This is the #1 source of errors in workflows!** Every operator (Generate, Revise, Summarize, Ensemble) returns a STRING, not a dictionary, list, or any other data structure.

❌ **WRONG - These will ALL cause TypeError:**
```python
# Trying to access string as dictionary
result = await self.generate(instruction="Return JSON", context="")
value = result["key"]  # TypeError!

# Trying to access string as list
items = await self.generate(instruction="List items", context="")
first = items[0]  # TypeError unless you mean first character!

# Assuming structured data
data = await self.generate(instruction="Return data", context="")
for item in data:  # This iterates over characters, not items!
```

✅ **CORRECT - How to handle operator outputs:**
```python
# Option 1: Parse JSON if you need structured data
import json  # Add this at the start of run_workflow
json_str = await self.generate(instruction="Return valid JSON", context="")
data = json.loads(json_str)  # Now it's a dict/list

# Option 2 (PREFERRED): Request simple text
name = await self.generate(
    instruction="Return ONLY the function name, nothing else",
    context=""
)
# 'name' is now a simple string like "calculate_sum"

# Option 3: Use string operations
result = await self.generate(instruction="List items separated by commas", context="")
items = result.split(",")  # Convert string to list
```

#### 🔑 **Understanding Parameters**

**The `instruction` Parameter (Required for all operators):**
- **Purpose:** Contains the COMPLETE strategic directive that fully specifies what the operator should do
- **Content:** Should be **comprehensive and detailed** - think of it as a full prompt that leaves nothing ambiguous
- **Length:** Can and SHOULD be long when needed (100-500+ words is perfectly acceptable and often necessary)
- **Dynamic Construction:** Can include information extracted from previous steps using f-strings
- **Key Principle:** Instructions guide the operation; context provides the data

**The `context` Parameter (Required for all operators except Generate):**
- **Purpose:** Provides the INPUT DATA that the instruction will operate on
- **Content:** The actual text, data, or results from previous operations
- **Type:** String for Generate/Revise/Summarize operators
- **Usage:** Think of it as the "working material" that the instruction processes
- **Note:** Ensemble uses `contexts` (plural) which takes List[str] instead of a single string

### Core Operators

**1. Generate: CREATE new information**
- **Signature:** `await self.generate(instruction: str, context: str = "") -> str`
- **Returns:** STRING (always!)
- **Purpose:** Produces new text, analysis, or reasoning based on strategic instructions

**2. Revise: IMPROVE existing information**
- **Signature:** `await self.revise(instruction: str, context: str) -> str`
- **Returns:** STRING (always!)
- **Purpose:** Critiques and refines existing text based on specific improvement criteria

**3. Summarize: COMPRESS information**
- **Signature:** `await self.summarize(instruction: str, context: str) -> str`
- **Returns:** STRING (always!)
- **Purpose:** Condenses text while preserving key information relevant to the problem

**4. Ensemble: DECIDE between or synthesize options**
- **Signature:** `await self.ensemble(instruction: str, contexts: List[str]) -> str`
- **Returns:** STRING (always!)
- **Purpose:** Evaluates, compares, or merges multiple candidate solutions

### 3. Key Design Principles

**Import Management:**
```python
async def run_workflow(self):
    import asyncio
    import json  # Import here if you need JSON parsing
    import re    # Import here if you need regex
    # Add all imports at the beginning of run_workflow
```

**Dynamic Instruction Construction:**
```python
# Extract as simple text, then embed in f-strings
func_name = await self.generate(
    instruction="Extract only the function name from test cases",
    context=""
)
code = await self.generate(
    instruction=f"Write a function named '{func_name}' that solves this",
    context=""
)
```

**Parallel Execution:**
```python
results = await asyncio.gather(
    self.generate(instruction="Approach 1...", context=""),
    self.generate(instruction="Approach 2...", context="")
)
final = await self.ensemble(instruction="Select best...", contexts=results)
```

**Common Pitfalls:**
- ❌ Don't assume operators return anything other than strings
- ❌ Don't forget to import modules (json, re, etc.) inside run_workflow
- ❌ Don't hardcode problem-specific data in workflow code
- ✅ Do parse JSON strings with json.loads() if needed
- ✅ Do prefer simple text extraction over complex JSON
- ✅ Do use detailed instructions (100-500+ words when needed)

### 4. Your Task: Complete the `run_workflow` Method

Your task is to write the Python code for the `run_workflow` method within the provided template. Focus on creating a robust, reusable workflow that leverages detailed instructions.

**Base Template:**
<think>
[Your step-by-step reasoning about the workflow strategy, why you chose specific operators, and how you'll use instructions effectively. Remember that all operators return strings!]
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
        - ALL operators return STRINGS
        - Import modules (json, re, etc.) at the beginning
        - Use detailed, comprehensive instructions
        - Parse JSON with json.loads() if needed
        """
        import asyncio
        # import json  # Uncomment if you need JSON parsing
        # import re    # Uncomment if you need regex
        
        # --- YOUR WORKFLOW LOGIC HERE ---
        # Remember: all operator outputs are strings!
</code>

### 5. Critical Rules

**A. Return Types:** ALL operators return STRINGS - parse with json.loads() if needed
**B. Imports:** Add all needed imports (json, re, etc.) at start of run_workflow
**C. Instructions:** Use comprehensive, detailed instructions (100-500+ words OK)
**D. Parameters:** `instruction` (str) + `context` (str) for most; `contexts` (List[str]) for Ensemble
**E. Control Flow:** Branch on operator results, not direct problem_text parsing
**F. Response Format:** ONLY `<think>...</think>` followed by `<code>...</code>`

### 6. Illustrative Example(s)

The following examples help you understand the problem type. Create a workflow for the *class* of problems, not just these instances.

'''