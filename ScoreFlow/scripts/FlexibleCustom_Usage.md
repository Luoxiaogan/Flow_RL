# FlexibleCustom Operator Usage Guide

## Overview

The `FlexibleCustom` operator is designed to enhance workflow diversity while maintaining the constraint of not including problem-specific information in LLM prompts. It allows workflows to define custom reasoning patterns and generation strategies dynamically.

## GSM8K FlexibleCustom Operator

### Basic Usage

```python
from ScoreFlow.scripts.gsm8k.operator import FlexibleCustom

# Create operator with different reasoning patterns
operator = FlexibleCustom(
    llm=llm_instance,
    problem=problem_data,
    reasoning_pattern="sequential",  # or "parallel", "iterative", "branching"
    steps=["analyze", "plan", "solve", "verify"],
    max_iterations=3,
    use_structured_output=True
)

# Execute the operator
result = await operator(
    custom_instruction="Focus on breaking down the problem systematically",
    previous_results=None
)
```

### Reasoning Patterns

1. **Sequential**: Step-by-step reasoning through defined steps
2. **Parallel**: Consider multiple approaches simultaneously  
3. **Iterative**: Refine solution through multiple iterations
4. **Branching**: Explore different solution paths

### Example Workflow

```python
# In workflow generation
custom_op = FlexibleCustom(
    llm=llm,
    problem=problem,
    reasoning_pattern="iterative",
    steps=["initial_analysis", "mathematical_modeling", "calculation", "verification"],
    max_iterations=2
)

solution = await custom_op("Apply algebraic approach with careful unit conversion")
```

## HumanEval FlexibleCustom Operator

### Basic Usage

```python
from ScoreFlow.scripts.humaneval.operator import FlexibleCustom

# Create operator for code generation
operator = FlexibleCustom(
    llm=llm_instance,
    problem=problem_data,
    generation_pattern="incremental",  # or "test_driven", "modular", "recursive"
    strategies=["understand", "design", "implement", "optimize"],
    max_refinements=3,
    use_structured_output=True
)

# Execute the operator
code = await operator(
    custom_approach="Implement with focus on edge case handling",
    previous_attempts=None
)
```

### Generation Patterns

1. **Incremental**: Build solution incrementally with refinements
2. **Test_driven**: Design based on test case analysis
3. **Modular**: Break into modular components
4. **Recursive**: Apply recursive problem-solving approach

### Example Workflow

```python
# In workflow generation
custom_code_op = FlexibleCustom(
    llm=llm,
    problem=problem,
    generation_pattern="test_driven",
    strategies=["analyze_tests", "design_algorithm", "implement_solution", "handle_edge_cases"],
    max_refinements=2
)

code_solution = await custom_code_op("Prioritize correctness over optimization")
```

## Workflow Generation Examples

### GSM8K Workflow with FlexibleCustom

```python
async def solve_with_flexible_pattern(problem):
    # Use iterative pattern for complex problems
    flexible_solver = FlexibleCustom(
        llm=llm,
        problem=problem,
        reasoning_pattern="iterative",
        steps=["decompose", "model", "calculate", "validate"],
        max_iterations=3
    )
    
    # First iteration
    solution = await flexible_solver("Break down into subproblems")
    
    # Review the solution
    reviewer = Review(llm=llm, problem=problem)
    reviewed_solution = await reviewer(solution)
    
    return reviewed_solution
```

### HumanEval Workflow with FlexibleCustom

```python
async def generate_code_flexibly(problem):
    # Use incremental pattern for code generation
    code_gen = FlexibleCustom(
        llm=llm,
        problem=problem,
        generation_pattern="incremental",
        strategies=["prototype", "enhance", "optimize", "finalize"],
        max_refinements=3
    )
    
    # Generate initial code
    code = await code_gen("Start with basic implementation")
    
    # Test the code
    runner = CodeRunner(llm=llm, problem=problem)
    test_result = await runner(code)
    
    if "FAILED" in test_result:
        # Use CodeFix with error info
        fixer = CodeFix(llm=llm, problem=problem)
        code = await fixer(code, test_result)
    
    return code
```

## Benefits

1. **Workflow Diversity**: Different reasoning patterns create diverse workflows
2. **No Problem Leakage**: Custom instructions don't include problem details
3. **Flexible Configuration**: Easily adjust patterns and steps
4. **Iterative Improvement**: Support for multi-iteration refinement
5. **Structured Output**: Optional structured responses for better parsing

## Best Practices

1. Choose reasoning patterns based on problem complexity
2. Define clear, actionable steps
3. Use custom instructions to guide approach without revealing problem details
4. Leverage iterative patterns for complex problems
5. Combine with other operators (Review, ScEnsemble) for robustness

## Integration Notes

- The FlexibleCustom operator is compatible with existing operator_an and op_prompt structures
- It can be used as a drop-in replacement for the basic Custom operator
- Works seamlessly with MetaGPT's ActionNode framework
- Supports both structured (XML) and simple fill modes