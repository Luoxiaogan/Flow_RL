# Workflow ID: mbppplus_154_0
# Benchmark: mbppplus
# Data Indices: [99, 230]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)
        self.programmer = operator.Programmer(self.llm, self.problem_text)
        self.decompose = operator.Decompose(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import re

        # Step 1: Deep problem analysis and intent extraction
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Extract:
            1. The core operation (e.g., counting, filtering, transforming, comparing)
            2. The data structures involved (list, tuple, set, string, etc.)
            3. The conditions or constraints (range, equality, pattern, etc.)
            4. Edge cases to consider (empty inputs, single elements, duplicates, type boundaries)
            5. Expected return type and structure
            6. Any implicit invariants or mathematical properties
            7. Whether the problem requires simple iteration or complex decomposition
            Present as a structured, bullet-point analysis with clear categorization.""",
            context=""
        )

        # Step 2: Classify problem complexity to determine branching
        complexity_assessment = await self.generate(
            instruction=f"""Based on this analysis:
            {problem_analysis}
            
            Classify the problem complexity:
            - SIMPLE: Can be solved with single-pass iteration or basic aggregation
            - COMPLEX: Requires multi-step logic, recursion, or decomposition
            - STATEFUL: Requires maintaining state or multiple passes
            - MATH_OPTIMIZABLE: Has mathematical shortcut or formula
            
            Also identify:
            - Primary data type (numeric, string, mixed)
            - Comparison type (equality, range, pattern, custom)
            - Order sensitivity (does order matter in input/output?)
            
            Return classification in format: "TYPE: [category], DATA: [type], COMPARISON: [type], ORDER: [sensitive/insensitive]".""",
            context=problem_analysis
        )

        # Step 3: Conditional branching based on complexity
        if "COMPLEX" in complexity_assessment or "STATEFUL" in complexity_assessment:
            # Decompose into subproblems
            subproblems = await self.decompose(
                instruction=f"""Break this problem into minimal, independent subproblems:
                - Each subproblem should be solvable in isolation
                - Define clear inputs and outputs for each
                - Specify dependencies between subproblems
                - Ensure base cases are explicitly handled
                - Subproblems should be granular enough for direct implementation""",
                context=problem_analysis
            )
            
            # Solve each subproblem recursively (simplified here as parallel generation)
            sub_solutions = []
            for sub in subproblems:
                sub_solution = await self.generate(
                    instruction=f"""Implement solution for subproblem:
                    {sub['description']}
                    Ensure it handles edge cases and matches expected output type.
                    Return only the function implementation with necessary imports.""",
                    context=problem_analysis
                )
                sub_solutions.append(sub_solution)
            
            # Synthesize final solution from sub-solutions
            final_implementation = await self.ensemble(
                instruction="""Synthesize a complete solution by integrating the subproblem solutions.
                Ensure:
                - Proper function signature matching original problem
                - Correct data flow between subproblems
                - Edge cases handled at integration points
                - Return type matches specification
                - Code is clean, readable, and efficient""",
                contexts_list=sub_solutions
            )
            
        else:
            # Generate multiple implementation strategies in parallel
            strategy_instructions = [
                """Implement using imperative loops (for/while). 
                Focus on explicit edge case handling and clear variable names.
                Include comments for key logic steps.""",
                
                """Implement using functional programming (comprehensions, filter, map).
                Focus on conciseness and readability.
                Ensure type consistency and proper aggregation.""",
                
                """Implement with mathematical optimization if applicable.
                Look for formulas or shortcuts that avoid full iteration.
                Include explanatory comments for the mathematical insight."""
            ]
            
            # Generate solutions in parallel
            solution_attempts = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""{instr}
                    
                    Problem context:
                    {problem_analysis}
                    
                    Complexity assessment:
                    {complexity_assessment}
                    
                    CRITICAL REQUIREMENTS:
                    - Match exact function signature from problem
                    - Handle empty inputs, single elements, duplicates
                    - Preserve expected return type (list/tuple/set)
                    - Use type-agnostic comparisons unless specified otherwise
                    - Include defensive checks for boundary conditions
                    - Return ONLY the function implementation with necessary imports""",
                    context=problem_analysis,
                    max_retries=3
                ) for instr in strategy_instructions]
            )
            
            # Ensemble: Select and synthesize best solution
            final_implementation = await self.ensemble(
                instruction="""Select and refine the best solution based on:
                1. Correctness (handles all edge cases explicitly)
                2. Readability (clear variable names, logical flow)
                3. Efficiency (avoids unnecessary operations)
                4. Robustness (type handling, boundary conditions)
                5. Signature compliance (exact parameter names, return type)
                
                If multiple solutions have strengths, synthesize a hybrid that combines their best aspects.
                Add any missing edge case handling or type checks.
                Ensure the final code is production-ready and passes implicit test suites.""",
                contexts_list=solution_attempts
            )

        # Final validation and refinement pass
        validated_implementation = await self.revise(
            instruction="""Critically review this implementation:
            - Verify function signature matches exactly (parameter names, order)
            - Check return type consistency
            - Ensure all edge cases are handled (empty, single, duplicates, boundaries)
            - Confirm type-agnostic operations where needed
            - Remove any debug prints or unnecessary comments
            - Optimize for clarity without sacrificing correctness
            
            Return ONLY the final, polished function implementation with necessary imports.
            No additional text or explanations.""",
            context=final_implementation
        )

        return validated_implementation