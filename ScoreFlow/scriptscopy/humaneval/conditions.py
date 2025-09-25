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
'''