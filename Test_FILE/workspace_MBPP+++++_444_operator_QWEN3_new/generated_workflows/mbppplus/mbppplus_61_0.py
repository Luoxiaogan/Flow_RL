# Workflow ID: mbppplus_61_0
# Benchmark: mbppplus
# Data Indices: [215, 116, 197]

class Workflow:
    def __init__(self, config, problem) -> None:
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        import asyncio
        import json

        # Phase 1: Parallel multi-perspective analysis
        math_analysis, struct_analysis, edge_analysis = await asyncio.gather(
            self.generate(
                instruction="""Analyze this problem from a mathematical perspective:
                - What formulas, equations, or numerical operations are required?
                - Are there statistical, arithmetic, or algebraic components?
                - What mathematical properties must be preserved?
                - Provide specific mathematical steps needed for solution.
                Format as bullet points with clear mathematical notation where applicable.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from a structural/data perspective:
                - What are the input and output data types? (list, tuple, set, etc.)
                - Are there mutability or immutability constraints?
                - What transformations or operations are needed on the data structures?
                - Are there ordering or uniqueness requirements?
                - Provide specific structural operations needed.
                Format as bullet points with clear data type specifications.""",
                context=""
            ),
            self.generate(
                instruction="""Analyze this problem from an edge-case perspective:
                - What are all possible boundary conditions? (empty inputs, single elements, etc.)
                - What invalid inputs might be provided? How should they be handled?
                - Are there type coercion issues or overflow/underflow risks?
                - What are the minimal and maximal valid inputs?
                - List specific edge cases that must be handled.
                Format as bullet points with concrete examples where possible.""",
                context=""
            )
        )

        # Phase 2: Synthesize unified problem specification
        problem_spec = await self.ensemble(
            instruction="""Synthesize these three analyses into a single, comprehensive problem specification.
            Create a structured outline with these sections:
            1. MATHEMATICAL_REQUIREMENTS: List all formulas, operations, and numerical properties
            2. STRUCTURAL_REQUIREMENTS: Specify input/output types and data transformations
            3. EDGE_CASES: List all boundary conditions and error handling requirements
            4. SOLUTION_STRATEGY: Recommend 1-3 appropriate solution approaches (imperative, functional, mathematical)
            Format as a JSON-like structure with clear section headers and bullet points.""",
            contexts_list=[math_analysis, struct_analysis, edge_analysis]
        )

        # Phase 3: Generate multiple solution candidates in parallel
        imperative_sol, functional_sol, mathematical_sol = await asyncio.gather(
            self.generate(
                instruction=f"""Generate an IMPERATIVE solution (using loops, conditionals):
                Problem Specification:
                {problem_spec}
                
                Requirements:
                - Use explicit loops and conditionals
                - Handle all edge cases specified
                - Match exact input/output types
                - Include comments explaining key steps
                - Return the correct data type as specified
                Format as complete Python function with proper signature.""",
                context=problem_spec
            ),
            self.generate(
                instruction=f"""Generate a FUNCTIONAL solution (using built-ins, comprehensions):
                Problem Specification:
                {problem_spec}
                
                Requirements:
                - Use Python built-ins (sum, map, filter, etc.) where appropriate
                - Use list/tuple comprehensions if applicable
                - Handle all edge cases specified
                - Match exact input/output types
                - Include comments explaining key steps
                - Return the correct data type as specified
                Format as complete Python function with proper signature.""",
                context=problem_spec
            ),
            self.generate(
                instruction=f"""Generate a MATHEMATICAL solution (formula-driven):
                Problem Specification:
                {problem_spec}
                
                Requirements:
                - Use mathematical formulas and direct calculations
                - Avoid unnecessary loops if formula exists
                - Handle all edge cases specified
                - Match exact input/output types
                - Include comments explaining mathematical steps
                - Return the correct data type as specified
                Format as complete Python function with proper signature.""",
                context=problem_spec
            )
        )

        # Phase 4: Revise each solution candidate (up to 2 iterations)
        solutions = [imperative_sol, functional_sol, mathematical_sol]
        revised_solutions = []
        
        for sol in solutions:
            current_sol = sol
            for iteration in range(2):  # Maximum 2 revision passes
                revised = await self.revise(
                    instruction=f"""Critically revise this solution:
                    Problem Specification:
                    {problem_spec}
                    
                    Revision Criteria:
                    1. CORRECTNESS: Does it implement the required operations correctly?
                    2. EDGE CASES: Does it handle all specified edge cases?
                    3. TYPE CONSISTENCY: Does it use correct input/output types?
                    4. EFFICIENCY: Is it reasonably efficient for the problem size?
                    5. READABILITY: Is the code clear and well-commented?
                    
                    If any issues are found, fix them. If no issues, return unchanged.
                    Return the complete revised Python function.""",
                    context=current_sol
                )
                # Only update if revision made substantive changes
                if revised.strip() != current_sol.strip():
                    current_sol = revised
                else:
                    break  # No changes needed, exit early
            revised_solutions.append(current_sol)

        # Phase 5: Ensemble select best solution
        final_solution = await self.ensemble(
            instruction="""Select the best solution from these candidates:
            Evaluation Criteria (in order of priority):
            1. ROBUSTNESS: Handles all edge cases correctly
            2. CORRECTNESS: Implements required operations accurately
            3. EFFICIENCY: Most computationally efficient
            4. READABILITY: Cleanest, most maintainable code
            5. STYLE: Matches problem's implied style (if reference solution exists)
            
            Return ONLY the selected complete Python function. Do not include any other text.""",
            contexts_list=revised_solutions
        )

        # Phase 6: Adversarial validation (final quality gate)
        validation = await self.generate(
            instruction=f"""Adversarial validation - try to break this solution:
            Solution to critique:
            {final_solution}
            
            Problem Specification:
            {problem_spec}
            
            Task: Assume this solution is wrong. What edge case, type error, or logical flaw could break it?
            - Test with extreme values, empty inputs, type mismatches, etc.
            - If you find a flaw, describe it concretely.
            - If no flaw found after thorough testing, respond with exactly: "VALID"
            
            Be brutally honest and exhaustive in your testing.""",
            context=final_solution
        )

        # If validation finds issues, do one final revision
        if "VALID" not in validation.upper():
            final_solution = await self.revise(
                instruction=f"""Final revision based on adversarial feedback:
                Adversarial Feedback:
                {validation}
                
                Problem Specification:
                {problem_spec}
                
                Fix all issues identified in the adversarial feedback.
                If no fix is possible, return the original solution.
                Return the complete revised Python function.""",
                context=final_solution
            )

        return final_solution