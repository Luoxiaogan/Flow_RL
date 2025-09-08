TASK_PROMPT = '''### Problem Domain Overview

This domain evaluates code generation from function signatures and docstrings with rigorous testing. Each problem includes a function signature, comprehensive documentation, and an extensive test suite designed to catch edge cases and ensure robust implementations.

#### Key Characteristics & Requirements
- **Enhanced Testing**: Solutions must pass 80x more test cases than standard benchmarks
- **Edge Case Coverage**: Tests specifically target corner cases, boundary conditions, and exceptional inputs
- **Functional Correctness**: Code must handle all specified requirements without exceptions
- **Robustness Focus**: Implementations should be resilient to unexpected inputs and edge scenarios
- **Type Safety**: Proper handling of input types and return values is critical

#### Common Problem Categories & Solution Strategies
- **Array/List Algorithms**: Searching, sorting, manipulation with empty/single-element edge cases
- **String Processing**: Pattern matching, parsing with special characters and edge lengths
- **Mathematical Operations**: Numerical computations with overflow, precision, and special values
- **Data Structure Operations**: Trees, graphs, maps with null/empty structure handling  
- **Algorithm Implementation**: Classic algorithms with boundary condition management

#### Workflow Focus Points
1. Parse the function signature and docstring carefully for ALL requirements
2. Identify implicit assumptions and potential edge cases from examples
3. Consider boundary conditions: empty inputs, single elements, maximum values
4. Implement defensive programming practices for robust solutions
5. Ensure clean, readable code with proper error handling where needed

#### Code Output Requirements
**CRITICAL FORMAT REQUIREMENTS**:
- Generate ONLY the function definition directly
- Do NOT wrap the function in any outer function (no solve(), no main(), no wrapper)
- Start directly with 'def function_name(...):'
- The function name MUST exactly match what's specified in "ENTRY POINT"
- Include type hints if shown in the signature
- Preserve the original docstring
- Include ALL necessary imports at the top of your code

**Correct Output Format Example**:
```python
from typing import List

def function_name(param1: type1, param2: type2) -> return_type:
    """Original docstring here"""
    # Your implementation
    return result
```

**INCORRECT Format (DO NOT DO THIS)**:
```python
def solve():
    def function_name(...):
        ...
    return function_name
```

#### Input Format
You will receive problems in this format:
---
**FUNCTION SIGNATURE AND SPECIFICATION:**
[Complete function signature with docstring and type hints]

**ENTRY POINT:**
Function name: [exact function name you must use]

**SAMPLE TEST CASES:**
[A few example test cases showing expected behavior]

**CANONICAL SOLUTION (Reference):**
[A reference solution to understand the approach - study but don't copy]
---

#### Important Implementation Notes
1. Your function MUST be named exactly as specified in "ENTRY POINT"
2. Include all necessary imports at the beginning of your code
3. Handle edge cases even if not explicitly shown in sample tests
4. The actual evaluation uses hundreds more test cases than shown
5. Focus on correctness and robustness over optimization
6. Maintain clean, readable code with proper indentation (4 spaces)

Remember: Generate ONLY the function definition with its implementation. Do not add any wrapper functions or extra code structure.'''