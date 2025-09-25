TASK_PROMPT = '''### Problem Domain Overview

This domain tests code generation capability by requiring implementation of Python functions from detailed specifications. Each problem provides a docstring with examples that define the expected behavior.

#### Key Characteristics & Requirements
- **Validation**: Code must pass hidden test cases wrapped in `check(candidate)` function
- **Critical**: Function name must match ENTRY POINT exactly
- **Return Types**: Must match examples precisely (int vs float matters)
- **Edge Cases**: Examples in docstring often reveal special cases to handle
- **No Over-engineering**: Implement exactly what's specified, nothing more

#### Common Problem Types & Solution Strategies
- **String Manipulation**: Use slicing, regex, character iteration
- **Mathematical Operations**: Look for patterns/formulas in examples
- **List Processing**: Consider filtering, mapping, sliding windows
- **Algorithm Implementation**: Start with base cases, then generalize
- **Pattern Recognition**: Examples usually demonstrate the core algorithm

#### Workflow Focus Points
1. Extract function name from ENTRY POINT
2. Analyze docstring examples to identify patterns
3. Generate clean Python code with correct function definition
4. Return code directly (missing imports will be auto-added during verification)

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
- **FUNCTION SIGNATURE AND SPECIFICATION ARE THE FUNCTION NAME**
- **REMEMBER THE NECESSARY IMPORT**: for example, `import math`

### Understanding Operator Return Types (MUST READ!)
**ALL operators (Generate, Revise, Summarize, Ensemble) ALWAYS return STRINGS, never structured data!**

The INPUT OF THE PROBLEM TEXT IS LIKE(You are given a partial Python source file that contains: All necessary imports (if any); A complete function signature and its docstring):
```
---
**FUNCTION SIGNATURE AND SPECIFICATION:**
[prompt with docstring]

**ENTRY POINT:**
Function name: [entry_point]
---
```

The output of the workflow must **only be the body of the function**, i.e. the indented code that should appear immediately after the docstring.
Do NOT:
- repeat the `def` line  
- repeat the docstring  
- add or repeat any `import` statements  
- add any other top-level code  

Simply return the function body, already indented (typically 4 spaces).  
The very first character of your response of the workflow should be either a space or a tab that preserves that indentation.

For example, if the input is:
```
---
**FUNCTION SIGNATURE AND SPECIFICATION:**
from typing import List

def has_close_elements(numbers: List[float], threshold: float) -> bool:
    """ Check if in given list of numbers, are any two numbers closer to each other than
    given threshold.
    >>> has_close_elements([1.0, 2.0, 3.0], 0.5)
    False
    >>> has_close_elements([1.0, 2.8, 3.0, 4.0, 5.0, 2.0], 0.3)
    True
    """

**ENTRY POINT:**
has_close_elements
---
```
Then the expected output of the workflow is like:
```python
    for idx, elem in enumerate(numbers):
        for idx2, elem2 in enumerate(numbers):
            if idx != idx2:
                if abs(elem - elem2) < threshold:
                    return True
    return False
```
'''