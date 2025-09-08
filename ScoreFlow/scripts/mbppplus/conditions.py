# ScoreFlow/scripts/mbppplus/conditions.py

TASK_PROMPT = '''### Problem Domain Overview

This domain evaluates fundamental programming skills through practical problem-solving tasks with rigorous testing standards.

#### Key Characteristics & Requirements
- **Problem Focus**: Real-world programming challenges requiring algorithmic thinking
- **Enhanced Testing**: Each problem includes both basic assertions and comprehensive test suites with edge cases
- **Practical Skills**: Tests ability to implement common algorithms, data manipulations, and utility functions
- **Robustness**: Solutions must handle diverse inputs including edge cases, empty inputs, and boundary conditions
- **Clean Code**: Emphasis on readable, efficient Python implementations

#### Common Problem Categories
- **List/Tuple Operations**: Finding common elements, filtering, transformations
- **String Manipulation**: Pattern matching, parsing, formatting
- **Mathematical Computations**: Number theory, arithmetic operations, sequences
- **Data Structure Algorithms**: Searching, sorting, set operations
- **Logic Problems**: Conditional processing, validation, comparisons

#### Solution Strategy Guidelines
1. **Understand the Task**: Read the prompt carefully to grasp exact requirements
2. **Study Test Cases**: Analyze provided assertions to understand expected behavior
3. **Consider Edge Cases**: Think about empty inputs, single elements, duplicates
4. **Reference Solution**: Study the approach but implement your own version
5. **Type Handling**: Ensure proper handling of different data types (lists, tuples, sets)
6. **Error Prevention**: Write defensive code that handles unexpected inputs gracefully

#### Code Output Requirements
**CRITICAL FORMAT**:
- Generate ONLY the function implementation
- Use the EXACT function name from the reference code
- Include all necessary imports at the top
- Preserve function signatures including parameter names
- Do NOT wrap in any outer function or class
- Return appropriate data types as shown in tests

**Output Structure**:
```python
# Any necessary imports
import module_name

def function_name(param1, param2):
    # Your implementation
    return result
```

#### Input Format
Problems are presented in this format:
---
**TASK DESCRIPTION:**
[Problem statement explaining what the function should do]

**FUNCTION SIGNATURE:**
[Reference implementation showing function name and parameters]

**BASIC TEST CASES:(in the testing of the workflow, this will not be provided)**
[Assert statements showing expected behavior]

**REFERENCE SOLUTION:(in the testing of the workflow, this will not be provided)**
[Working solution to understand the approach - study but don't copy directly]

**NOTE:** The actual evaluation includes extensive additional test cases beyond those shown.
---

#### Implementation Best Practices
1. **Data Type Consistency**: Pay attention to whether the problem uses lists, tuples, or sets
2. **Return Type Matters**: Match the exact return type expected (tuple vs list vs set)
3. **Handle Empty Cases**: Always consider what happens with empty inputs
4. **Preserve Order**: Some problems care about order, others don't - check the tests
5. **Efficiency**: While correctness is primary, avoid unnecessarily inefficient solutions
6. **Clean Logic**: Write clear, understandable code with appropriate variable names

#### Common Pitfalls to Avoid
- Forgetting to handle empty inputs or single-element cases
- Mixing up data types (returning list when tuple expected)
- Not considering duplicate elements in collections
- Missing edge cases like negative numbers or special values
- Assuming input is always valid without checking

Remember: The shown test cases are just examples. Your solution will be tested against hundreds of additional cases including edge conditions, so write robust code that handles all possibilities correctly.'''