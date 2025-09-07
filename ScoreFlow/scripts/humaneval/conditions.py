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

#### Input Format
```
---
**FUNCTION SIGNATURE AND SPECIFICATION:**
[Complete function signature with docstring containing problem description and examples]

**ENTRY POINT:**
Function name: [exact function name to implement]
---
```
Multiple problems follow the same structure if provided.
```
'''