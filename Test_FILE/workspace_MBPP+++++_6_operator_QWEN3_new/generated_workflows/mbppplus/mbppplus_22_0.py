# Workflow ID: mbppplus_22_0
# Benchmark: mbppplus
# Data Indices: [196, 328]

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
        
        # Step 1: Comprehensive problem analysis
        problem_analysis = await self.generate(
            instruction="""Perform deep analysis of this programming problem:
            1. CLASSIFY the problem type: Is it mathematical, data structure manipulation, string processing, logical validation, or algorithmic?
            2. IDENTIFY key operations needed: What specific computations or transformations are required?
            3. ANTICIPATE edge cases: What boundary conditions, empty inputs, or special values might need handling?
            4. SUGGEST solution strategies: Propose 2-3 different approaches (e.g., mathematical formula, iterative solution, built-in methods)
            5. NOTE any constraints: Return type requirements, performance considerations, or specific Python features to use/avoid
            6. EXTRACT function signature: Identify the exact function name and parameters from the problem
            Provide structured, detailed analysis that will guide subsequent solution generation.""",
            context=""
        )

        # Step 2: Generate multiple solution approaches in parallel
        solution_approaches = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution using mathematical/formula-based approach:
                Based on this analysis: {problem_analysis}
                
                - Derive any necessary mathematical formulas
                - Focus on efficiency and elegance
                - Handle edge cases explicitly
                - Return code matching exact function signature
                - Include necessary imports at top
                - Code must be production-ready and pass rigorous tests""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using iterative/algorithmic approach:
                Based on this analysis: {problem_analysis}
                
                - Use clear, step-by-step logic
                - Prioritize readability and maintainability
                - Include comprehensive edge case handling
                - Return code matching exact function signature
                - Include necessary imports at top
                - Code must be production-ready and pass rigorous tests""",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using Python built-in methods and standard library:
                Based on this analysis: {problem_analysis}
                
                - Leverage Python's built-in functions and data structure methods
                - Focus on simplicity and Pythonic style
                - Ensure robust handling of edge cases
                - Return code matching exact function signature
                - Include necessary imports at top
                - Code must be production-ready and pass rigorous tests""",
                context=problem_analysis
            )
        )

        # Step 3: Ensemble - select best solution or synthesize
        selected_solution = await self.ensemble(
            instruction="""Evaluate and select the best solution from the candidates:
            CRITERIA:
            1. CORRECTNESS: Which solution most accurately implements the requirements?
            2. ROBUSTNESS: Which handles edge cases most comprehensively?
            3. EFFICIENCY: Which has the best time/space complexity?
            4. SIMPLICITY: Which is most readable and maintainable?
            5. TYPE SAFETY: Which best matches required return types and handles type conversions properly?
            
            If no single solution is clearly superior, synthesize a new solution combining the best elements of each.
            Return ONLY the final Python function implementation with proper imports, nothing else.""",
            contexts_list=solution_approaches
        )

        # Step 4: Validation and refinement loop
        refined_solution = selected_solution
        max_iterations = 3
        for i in range(max_iterations):
            validation = await self.generate(
                instruction=f"""Critically validate this solution:
                {refined_solution}
                
                CHECK FOR:
                1. Edge case handling (empty inputs, single elements, boundary values)
                2. Type consistency (return types, parameter types)
                3. Logical errors or off-by-one mistakes
                4. Performance bottlenecks
                5. Code style and readability
                6. Match to function signature requirements
                
                If serious issues found, provide specific revision instructions.
                If solution is robust and correct, respond with "VALIDATED: Solution meets all requirements."""",
                context=refined_solution
            )
            
            if "VALIDATED" in validation or "validated" in validation:
                break
            else:
                refined_solution = await self.revise(
                    instruction=f"""Revise the solution based on this feedback:
                    {validation}
                    
                    - Fix all identified issues
                    - Maintain function signature exactly
                    - Keep code clean and efficient
                    - Return complete Python implementation with imports""",
                    context=refined_solution
                )

        # Step 5: Final verification with programmer operator for syntax and basic correctness
        final_result = await self.programmer(
            instruction=f"""Generate and verify the final solution:
            Based on this refined implementation: {refined_solution}
            
            - Ensure syntactically correct Python code
            - Match exact function signature from problem
            - Include all necessary imports
            - Return only the function implementation, nothing else
            - Code must be ready for rigorous testing with edge cases""",
            context=refined_solution
        )

        # Extract just the code portion if programmer returns additional text
        code_lines = []
        in_code = False
        for line in final_result.split('\n'):
            if line.strip().startswith('