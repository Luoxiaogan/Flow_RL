# Workflow ID: mbppplus_102_0
# Benchmark: mbppplus
# Data Indices: [208, 100]

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

        # Phase 1: Deep Problem Analysis & Classification
        problem_analysis = await self.generate(
            instruction="""Perform a comprehensive analysis of this programming problem. Your analysis must include:
            1. Problem Category: Classify as one of: [List/Tuple Operations, String Manipulation, Mathematical Computation, Data Structure Algorithm, Logic Problem]
            2. Input/Output Specification: Detail expected input types, output types, and any constraints (e.g., must return tuple, handle empty lists)
            3. Key Algorithmic Patterns: Identify relevant patterns (e.g., two-pointer, prefix sum, element-wise comparison, recursion)
            4. Edge Cases: List all potential edge cases (empty inputs, single elements, duplicates, negative numbers, boundary conditions)
            5. Performance Requirements: Note any implied time/space complexity needs
            6. Solution Strategy Options: Propose 2-3 distinct high-level approaches to solve this
            Format your response as a structured markdown document with clear section headers.""",
            context=""
        )

        # Phase 2: Adaptive Strategy Selection
        strategy_decision = await self.generate(
            instruction=f"""Based on the following analysis, decide the optimal solution strategy:
            {problem_analysis}

            Choose ONE of the following paths:
            A) DIRECT_CODE: If the problem is simple, atomic, and requires no decomposition (e.g., element-wise comparisons, simple transforms)
            B) DECOMPOSE_THEN_SOLVE: If the problem involves state tracking, multiple steps, or complex logic (e.g., equilibrium index, multi-pass algorithms)
            C) PARALLEL_ALGORITHMS: If multiple non-trivial algorithmic approaches are viable and should be compared

            Respond ONLY with the letter (A, B, or C) followed by a colon and a one-sentence justification.""",
            context=problem_analysis
        )

        # Phase 3: Branch Based on Strategy
        if strategy_decision.startswith("A:"):
            # Direct code generation with rich context
            solution_code = await self.programmer(
                instruction=f"""Generate a robust, production-ready Python function that solves the problem.
                CONTEXT:
                {problem_analysis}

                REQUIREMENTS:
                - Use the EXACT function signature specified in the problem
                - Handle ALL edge cases mentioned in the analysis
                - Include type hints if appropriate
                - Prioritize readability and defensive programming
                - Return correct data type (list vs tuple vs int)
                - Add minimal but clear comments for complex logic
                - Do NOT include test cases or print statements
                """,
                context=problem_analysis,
                max_retries=3
            )
            
        elif strategy_decision.startswith("B:"):
            # Decompose into subproblems
            subproblems = await self.decompose(
                instruction=f"""Break this problem into minimal, executable subproblems. For each subproblem:
                - Must be solvable independently given its dependencies
                - Should represent a single logical operation
                - Must include input/output specifications
                - Must handle edge cases locally if applicable
                Base your decomposition on this analysis:
                {problem_analysis}""",
                context=problem_analysis
            )
            
            # Solve each subproblem in parallel
            subproblem_solutions = await asyncio.gather(
                *[self.programmer(
                    instruction=f"""Solve this subproblem as a standalone function or code snippet:
                    Subproblem: {sp['description']}
                    Dependencies: {sp.get('dependencies', 'None')}
                    
                    Guidelines:
                    - Assume dependencies are solved and available as functions/variables
                    - Handle edge cases specific to this subproblem
                    - Return appropriate data type
                    - Keep code minimal and focused""",
                    context=problem_analysis,
                    max_retries=2
                ) for sp in subproblems]
            )
            
            # Integrate subproblem solutions into final code
            solution_code = await self.generate(
                instruction=f"""Integrate these subproblem solutions into a complete, cohesive function:
                Subproblem Solutions:
                {''.join(f'--- Subproblem {i+1} ---\n{sol}\n' for i, sol in enumerate(subproblem_solutions))}
                
                Integration Requirements:
                - Use the exact function signature from the original problem
                - Ensure data flows correctly between subproblems
                - Handle any remaining edge cases at the top level
                - Optimize for readability and maintainability
                - Return the correct final data type
                - Do NOT include test cases or example usage""",
                context=problem_analysis
            )
            
        else:  # strategy_decision.startswith("C:")
            # Generate multiple algorithmic approaches in parallel
            algorithm_approaches = await asyncio.gather(
                self.programmer(
                    instruction=f"""Generate Solution Approach 1:
                    {problem_analysis}
                    Focus on simplicity and readability. Use straightforward logic even if less efficient.""",
                    context=problem_analysis,
                    max_retries=2
                ),
                self.programmer(
                    instruction=f"""Generate Solution Approach 2:
                    {problem_analysis}
                    Focus on optimal time/space complexity. Use advanced techniques if beneficial.""",
                    context=problem_analysis,
                    max_retries=2
                ),
                self.programmer(
                    instruction=f"""Generate Solution Approach 3:
                    {problem_analysis}
                    Focus on robustness and edge case handling. Add defensive checks and clear error handling.""",
                    context=problem_analysis,
                    max_retries=2
                )
            )
            
            # Ensemble: Select best approach
            solution_code = await self.ensemble(
                instruction="""Select the best solution from the candidates below based on:
                1. Correctness: Must handle all edge cases and match expected behavior
                2. Efficiency: Prefer O(n) over O(n^2) when possible
                3. Readability: Clear variable names and logical flow
                4. Robustness: Defensive programming and type safety
                5. Conciseness: Avoid unnecessary complexity
                
                Return ONLY the selected code with no additional commentary or markdown.""",
                contexts_list=algorithm_approaches
            )

        # Phase 4: Validation and Refinement Loop
        for iteration in range(3):
            validation_check = await self.generate(
                instruction=f"""Critically review this code for defects:
                {solution_code}
                
                Check for:
                - Off-by-one errors
                - Type mismatches (returning list instead of tuple, etc.)
                - Unhandled edge cases (empty inputs, single elements, duplicates)
                - Logical flaws in algorithm
                - Variable naming clarity
                - Adherence to function signature
                - Performance bottlenecks
                
                If no issues found, respond with "VALID: [brief confirmation]".
                If issues found, respond with "INVALID: [detailed description of each issue]". """,
                context=solution_code
            )
            
            if validation_check.startswith("VALID:"):
                break
            else:
                solution_code = await self.revise(
                    instruction=f"""Fix all issues identified in this validation report:
                    {validation_check}
                    
                    Original Problem Context:
                    {problem_analysis}
                    
                    Requirements:
                    - Preserve the core algorithm unless fundamentally flawed
                    - Fix ALL identified issues
                    - Maintain clean, readable code
                    - Do NOT introduce new features or complexity
                    - Return ONLY the corrected code with no additional text""",
                    context=solution_code
                )
        else:
            # Fallback: Generate ultra-defensive version
            solution_code = await self.programmer(
                instruction=f"""Generate a fallback solution that prioritizes correctness above all else:
                {problem_analysis}
                
                Guidelines:
                - Add explicit type checks and assertions
                - Handle every conceivable edge case with if-statements
                - Use verbose variable names for clarity
                - Include comments explaining each step
                - Sacrifice elegance for robustness
                - Return correct data type under all circumstances""",
                context=problem_analysis,
                max_retries=1
            )

        # Phase 5: Final Sanitization and Output
        final_code = await self.revise(
            instruction="""Finalize this code for submission:
            - Remove any markdown code block indicators (