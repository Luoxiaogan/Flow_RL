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
- **FUNCTION SIGNATURE AND SPECIFICATION ARE THE FUNCTION NAME**
- **REMEMBER THE NECESSARY IMPORT**: for example, `import math`

### Understanding Operator Return Types (MUST READ!)
**ALL operators (Generate, Revise, Summarize, Ensemble) ALWAYS return STRINGS, never structured data!**
'''