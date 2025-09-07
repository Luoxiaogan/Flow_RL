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

#### Workflow Focus Points
1. Extract function name from assert statements carefully
2. Parse natural language to understand all requirements
3. Identify edge cases from test examples
4. Generate complete, working Python code with proper imports
5. Validate code structure: proper indentation, complete imports, clean syntax

#### Code Output Requirements
**CRITICAL**: Your final answer should contain Python code in ONE of these formats:

**Format 1 (Preferred)**: Markdown code block
```python
import math  # Include all necessary imports

def function_name(args):
    # Proper 4-space indentation
    result = computation
    return result
```

**Format 2**: Direct code (if not using markdown)
```
import math

def function_name(args):
    # Still maintain proper indentation
    result = computation
    return result
```

**Important Notes**:
- The code extractor looks for ```python blocks first, then falls back to raw code
- Preserve ALL indentation - use exactly 4 spaces per level
- Include ALL necessary imports at the top of the code
- The function name MUST match what appears in the assert statements
- Code should be complete and executable without modifications

#### Input Format
```
---
**TASK:**
[Natural language description of the programming task]

**TEST CASES:(for you to know the function name and expected input types from arguments)**
assert function_name(args) == expected_output
assert function_name(args) == expected_output
assert function_name(args) == expected_output
---
```
Multiple problems follow the same structure if provided.
'''