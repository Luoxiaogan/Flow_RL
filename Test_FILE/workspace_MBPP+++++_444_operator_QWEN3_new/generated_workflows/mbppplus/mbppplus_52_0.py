# Workflow ID: mbppplus_52_0
# Benchmark: mbppplus
# Data Indices: [212, 317, 120]

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
        import re

        # Phase 1: Problem Classification & Decomposition
        problem_analysis = await self.generate(
            instruction="""Perform deep problem analysis. Classify the problem type and extract critical components.
            1. Identify primary domain: string, numerical, DP, grid, set/list, graph, or other.
            2. Extract key parameters and their expected types.
            3. Determine return type and format (list, tuple, int, float, etc.).
            4. Identify potential edge cases: empty inputs, single elements, zeros, negatives, duplicates.
            5. Note any explicit or implicit constraints.
            6. Suggest 2-3 possible algorithmic approaches.
            Format as structured markdown with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Solution Generation from Multiple Perspectives
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate solution from MATHEMATICAL/ALGORITHMIC perspective.
                Problem Analysis: {problem_analysis}
                
                Focus on:
                - Deriving formulas or recurrence relations
                - Proving correctness through invariants
                - Optimizing for time/space complexity
                - Using appropriate data structures
                - Including detailed comments explaining logic
                Return ONLY the function implementation with imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution from STRUCTURAL/DATA-FLOW perspective.
                Problem Analysis: {problem_analysis}
                
                Focus on:
                - Step-by-step transformation of inputs to outputs
                - Intermediate data structures and their purposes
                - Clear variable naming reflecting data roles
                - Handling of data type conversions
                - Explicit management of state changes
                Return ONLY the function implementation with imports, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate solution from EDGE-CASE/DEFENSIVE perspective.
                Problem Analysis: {problem_analysis}
                
                Focus on:
                - Explicit handling of all edge cases mentioned in analysis
                - Input validation and type checking
                - Guard clauses for empty/null inputs
                - Boundary condition testing within code
                - Fallback behaviors and error prevention
                Return ONLY the function implementation with imports, nothing else.""",
                context=""
            )
        )

        # Phase 3: Ensemble Synthesis - Merge best aspects of all solutions
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize a unified solution from the three provided attempts.
            CRITICAL RULES:
            - Preserve exact function signature from original problem
            - Combine mathematical rigor with structural clarity and defensive robustness
            - Adopt the most comprehensive edge-case handling
            - Choose the clearest variable names and code structure
            - Ensure return type matches problem requirements exactly
            - Remove any redundant or conflicting logic
            - Add comments only if they clarify non-obvious logic
            Return ONLY the function implementation with imports, nothing else.""",
            contexts_list=solution_attempts
        )

        # Phase 4: Iterative Validation and Refinement (up to 3 iterations)
        current_solution = synthesized_solution
        for iteration in range(3):
            # Generate critique focused on common pitfalls
            critique = await self.generate(
                instruction=f"""Critically analyze this solution for flaws and improvements.
                Current Solution: {current_solution}
                
                Check for:
                - Off-by-one errors
                - Type mismatches (list vs tuple, int vs float)
                - Unhandled edge cases (empty inputs, single elements, zeros, negatives)
                - Performance bottlenecks
                - Deviations from expected return format
                - Missing input validation
                - Logical errors in algorithm implementation
                - Variable naming clarity
                Provide specific, actionable feedback. If no issues found, state "NO ISSUES FOUND".""",
                context=current_solution
            )
            
            # If no issues found, break early
            if "NO ISSUES FOUND" in critique.upper():
                break
                
            # Revise based on critique
            current_solution = await self.revise(
                instruction=f"""Revise the solution to address the following critique:
                Critique: {critique}
                
                Specific revision requirements:
                - Fix all identified issues
                - Maintain exact function signature
                - Preserve core algorithmic logic while correcting flaws
                - Add necessary edge case handling
                - Ensure return type matches requirements exactly
                - Keep code clean and readable
                Return ONLY the function implementation with imports, nothing else.""",
                context=current_solution
            )

        # Phase 5: Final Invariant Extraction and Validation
        invariant = await self.summarize(
            instruction=f"""Extract the core invariant or correctness condition for this solution.
            Current Solution: {current_solution}
            
            What must always be true for this solution to work correctly?
            Examples: 
            - "DP table must be initialized with base case table[0][i] = 1"
            - "Loop must iterate exactly n times where n is input length"
            - "Return value must be float with exactly one decimal place"
            Return a single, precise sentence describing the critical invariant.""",
            context=current_solution
        )

        # Final validation against invariant
        final_check = await self.generate(
            instruction=f"""Verify that the solution satisfies this invariant: {invariant}
            Solution: {current_solution}
            
            If invariant is satisfied, return the solution unchanged.
            If not, revise to ensure invariant is satisfied.
            Return ONLY the function implementation with imports, nothing else.""",
            context=current_solution
        )

        return final_check