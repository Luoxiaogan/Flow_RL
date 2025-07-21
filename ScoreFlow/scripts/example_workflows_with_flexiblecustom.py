"""
Example workflows using the FlexibleCustom operator to demonstrate
how to generate diverse workflows without embedding problem information.
"""

# GSM8K Example Workflows

async def gsm8k_sequential_workflow(problem, llm):
    """Sequential reasoning workflow for mathematical problems."""
    # Step 1: Analyze with custom sequential pattern
    analyzer = FlexibleCustom(
        llm=llm,
        problem=problem,
        reasoning_pattern="sequential",
        steps=["identify_knowns", "identify_unknowns", "select_approach", "solve_step_by_step"],
        use_structured_output=True
    )
    initial_solution = await analyzer("Focus on systematic breakdown of the problem")
    
    # Step 2: Verify with code
    programmer = Programmer(llm=llm, problem=problem)
    code_verification = await programmer(initial_solution)
    
    # Step 3: Review final solution
    reviewer = Review(llm=llm, problem=problem)
    final_solution = await reviewer(code_verification)
    
    return final_solution


async def gsm8k_iterative_workflow(problem, llm):
    """Iterative refinement workflow for complex problems."""
    # Use iterative pattern with multiple rounds
    solver = FlexibleCustom(
        llm=llm,
        problem=problem,
        reasoning_pattern="iterative",
        steps=["initial_approach", "refine_method", "calculate_precisely", "double_check"],
        max_iterations=3,
        use_structured_output=True
    )
    
    # First iteration with broad approach
    solution = await solver("Start with high-level understanding")
    
    # Use reflection to guide next iteration
    reflector = Reflect(llm=llm, problem=problem)
    reflection = await reflector(solution)
    
    # Second iteration with reflection insights
    refined_solution = await solver(f"Refine based on reflection: {reflection[:100]}...")
    
    return refined_solution


async def gsm8k_ensemble_workflow(problem, llm):
    """Ensemble workflow using different reasoning patterns."""
    solutions = []
    
    # Approach 1: Sequential algebraic
    solver1 = FlexibleCustom(
        llm=llm, problem=problem,
        reasoning_pattern="sequential",
        steps=["algebraic_setup", "equation_formulation", "algebraic_solution", "numerical_answer"]
    )
    solutions.append(await solver1("Use algebraic approach with variable definitions"))
    
    # Approach 2: Parallel consideration
    solver2 = FlexibleCustom(
        llm=llm, problem=problem,
        reasoning_pattern="parallel",
        steps=["arithmetic_method", "algebraic_method", "logical_deduction", "pattern_recognition"]
    )
    solutions.append(await solver2("Consider multiple solution methods simultaneously"))
    
    # Approach 3: Custom with specific focus
    solver3 = Custom(llm=llm, problem=problem)
    solutions.append(await solver3("Solve by working backwards from the answer"))
    
    # Ensemble the solutions
    ensemble = ScEnsemble(llm=llm, problem=problem)
    best_solution = await ensemble(solutions)
    
    return best_solution


# HumanEval Example Workflows

async def humaneval_incremental_workflow(problem, llm):
    """Incremental code generation with testing."""
    # Generate code incrementally
    code_gen = FlexibleCustom(
        llm=llm,
        problem=problem,
        generation_pattern="incremental",
        strategies=["skeleton", "core_logic", "edge_cases", "optimization"],
        max_refinements=3,
        use_structured_output=True
    )
    
    # Start with basic structure
    code = await code_gen("Begin with function skeleton and basic logic")
    
    # Test initial implementation
    runner = CodeRunner(llm=llm, problem=problem)
    test_result = await runner(code)
    
    if "FAILED" in test_result:
        # Refine based on test failure
        code = await code_gen(f"Fix based on test failure", [code])
    
    # Final review
    reviewer = Review(llm=llm, problem=problem)
    final_code = await reviewer(code)
    
    return final_code


async def humaneval_test_driven_workflow(problem, llm):
    """Test-driven development workflow."""
    # Use test-driven pattern
    tdd_gen = FlexibleCustom(
        llm=llm,
        problem=problem,
        generation_pattern="test_driven",
        strategies=["understand_tests", "minimal_implementation", "handle_failures", "refactor"],
        use_structured_output=True
    )
    
    # Generate based on test understanding
    code = await tdd_gen("Analyze expected behavior from problem description")
    
    # Run tests
    runner = CodeRunner(llm=llm, problem=problem)
    result = await runner(code)
    
    if "FAILED" in result:
        # Use CodeFix for targeted fixes
        fixer = CodeFix(llm=llm, problem=problem)
        code = await fixer(code, result)
    
    return code


async def humaneval_modular_workflow(problem, llm):
    """Modular code generation workflow."""
    # Generate modular code
    modular_gen = FlexibleCustom(
        llm=llm,
        problem=problem,
        generation_pattern="modular",
        strategies=["identify_components", "implement_helpers", "integrate_main", "polish"],
        use_structured_output=True
    )
    
    # Create modular solution
    code = await modular_gen("Break down into helper functions if complexity warrants")
    
    # Standard code generation for comparison
    standard_gen = CustomCodeGenerate(llm=llm, problem=problem)
    standard_code = await standard_gen("Generate efficient solution")
    
    # Compare and select better approach
    solutions = [code, standard_code]
    ensemble = ScEnsemble(llm=llm, problem=problem)
    best_code = await ensemble(solutions)
    
    # Final test
    runner = CodeRunner(llm=llm, problem=problem)
    test_result = await runner(best_code)
    
    return best_code if "PASSED" in test_result else code


# Advanced Workflow Patterns

async def adaptive_workflow(problem, llm, benchmark_type="gsm8k"):
    """Adaptive workflow that changes strategy based on problem characteristics."""
    if benchmark_type == "gsm8k":
        # Analyze problem complexity (this is just an example heuristic)
        analyzer = FlexibleCustom(
            llm=llm, problem=problem,
            reasoning_pattern="sequential",
            steps=["complexity_assessment"],
            use_structured_output=False
        )
        complexity = await analyzer("Assess if this requires simple arithmetic or complex reasoning")
        
        # Choose workflow based on assessment
        if "complex" in complexity.lower() or "multiple steps" in complexity.lower():
            return await gsm8k_iterative_workflow(problem, llm)
        else:
            return await gsm8k_sequential_workflow(problem, llm)
    
    elif benchmark_type == "humaneval":
        # Start with test-driven to understand requirements
        tdd_result = await humaneval_test_driven_workflow(problem, llm)
        
        # If still failing, try incremental refinement
        runner = CodeRunner(llm=llm, problem=problem)
        if "FAILED" in await runner(tdd_result):
            return await humaneval_incremental_workflow(problem, llm)
        
        return tdd_result


# Workflow templates for generation

WORKFLOW_TEMPLATES = {
    "gsm8k": {
        "sequential": gsm8k_sequential_workflow,
        "iterative": gsm8k_iterative_workflow,
        "ensemble": gsm8k_ensemble_workflow,
    },
    "humaneval": {
        "incremental": humaneval_incremental_workflow,
        "test_driven": humaneval_test_driven_workflow,
        "modular": humaneval_modular_workflow,
    },
    "adaptive": adaptive_workflow
}