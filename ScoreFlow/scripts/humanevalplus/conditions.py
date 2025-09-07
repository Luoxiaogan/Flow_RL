TASK_PROMPT = '''### Problem Domain Overview

HumanEval+ (Enhanced HumanEval) tests problem-solving capabilities in the specified domain.

#### Key Characteristics & Requirements
- **Input:** Function signatures with detailed docstrings and examples
- **Output:** Complete Python function implementations
- **Skills:** Algorithm design, edge case handling, type hints, complex logic
- **Enhanced Testing:** Significantly more test cases than original HumanEval for robustness

#### Input Format
```
---
**PROBLEM:**
[Complete problem statement]
---
```
Multiple problems follow the same structure if provided.'''