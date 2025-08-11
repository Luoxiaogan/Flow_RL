TASK_PROMPT = '''### 1. Problem Domain Overview
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