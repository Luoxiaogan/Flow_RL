# ScoreFlow/scripts/mbpp/conditions.py
TASK_PROMPT = '''### Problem Domain Overview

This domain tests code generation from natural language descriptions. Each problem provides a task description and assert statements that the solution must satisfy.

#### Key Characteristics & Requirements
- **Validation**: Code must pass all assert statement test cases
- **Function Inference**: Must extract function name from test cases
- **Natural Language**: Task descriptions are informal, may be ambiguous
- **Entry-Level**: Problems designed for basic programming skills
- **Standard Library**: Often requires Python standard library functions

#### Common Problem Types & Solution Strategies
- **List/Array Operations**: Finding elements, computing sums, transformations
- **Mathematical Computations**: Prime numbers, GCD/LCM, combinatorics
- **String Manipulation**: Pattern matching, parsing, formatting
- **Data Structures**: Dictionary/set operations, basic algorithms
- **Standard Library Usage**: Leveraging built-in functions and modules

**Key Success Factors:**
- Understanding the exact requirements from the description
- Identifying all edge cases and constraints
- Writing clean, efficient, and correct Python code
- Ensuring the function signature matches test expectations
- Handling type conversions and input validation appropriately
- **Including all necessary import statements** (e.g., `import math`, `import re`, `from collections import Counter`)
- **TEST CASES GIVE THE FUNCTION NAME!, MAKE SURE THAT THE OUTPUT FUCNTION MATCH THE FUNCTION NAME!**

#### Code Output Requirements
**CRITICAL**: Your final answer should contain Python code in ONE of these formats:

**CRITICAL Workflow Design Considerations for MBPP:**

### Understanding Operator Return Types (MUST READ!)
**ALL operators (Generate, Revise, Summarize, Ensemble) ALWAYS return STRINGS, never structured data!**

**WRONG - This will cause TypeError:**
```python
import math  # Include all necessary imports

def function_name(args):
    # Proper 4-space indentation
    result = computation
    return result
```

**CORRECT Option 1 - Parse JSON string:**
```python
import json  # Remember to import json at the beginning of run_workflow
result_json = await self.generate(instruction="Return JSON with keys 'name' and 'age'", context="")
result = json.loads(result_json)  # Parse string to dict
name = result["name"]  # Now this works
```

**BETTER Option 2 - Use simple text (RECOMMENDED for MBPP):**
```python
# Ask for simple, directly usable text instead of JSON
func_name = await self.generate(
    instruction="Extract the function name from the test cases. Return ONLY the function name, nothing else.",
    context=""
)
# Now func_name is directly usable: "first_repeated_char"
```
---
**TASK:**
[Natural language description of the programming task]

**TEST CASES:(for you to know the function name and expected input types, testing of the workflow, this WILL be provided to the workflow, since it is essential for understanding the function name)**
assert function_name(args) == expected_output
assert function_name(args) == expected_output
assert function_name(args) == expected_output

**REFERENCE ANSWER(code):(in the testing of the workflow, this will not be provided to the workflow)**
[reference solution code]
---
```

'''