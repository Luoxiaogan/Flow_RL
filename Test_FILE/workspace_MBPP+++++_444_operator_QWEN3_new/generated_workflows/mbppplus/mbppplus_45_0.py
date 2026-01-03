# Workflow ID: mbppplus_45_0
# Benchmark: mbppplus
# Data Indices: [165, 318, 115]

# --- DO NOT IMPORT HERE ---
class Workflow:
    def __init__(self, config, problem) -> None:
        # --- DO NOT MODIFY THIS SECTION ---
        self.config = config
        self.problem_text = problem
        self.llm = create(config)
        
        self.generate = operator.Generate(self.llm, self.problem_text)
        self.revise = operator.Revise(self.llm, self.problem_text)
        self.summarize = operator.Summarize(self.llm, self.problem_text)
        self.ensemble = operator.Ensemble(self.llm, self.problem_text)

    async def run_workflow(self):
        """
        Universal problem-solving workflow for programming challenges.
        Employs parallel strategy exploration, adversarial validation, and iterative refinement.
        """
        import asyncio
        import re

        # PHASE 1: MULTI-PERSPECTIVE DECOMPOSITION
        decomposition = await self.generate(
            instruction="""Perform deep problem decomposition. Analyze from three orthogonal perspectives:
            1. STRUCTURAL: Identify input/output data types, constraints, and invariants. What structures are involved (lists, tuples, sets, scalars)? Is order preserved? Are duplicates significant?
            2. MATHEMATICAL: What underlying mathematical relationships or patterns exist? Is this fundamentally additive, multiplicative, combinatorial, or geometric? Are there closed-form solutions?
            3. EDGE-CASE ROBUSTNESS: Enumerate all plausible edge conditions: empty inputs, singleton inputs, extreme values, type boundaries, ordering edge cases.
            
            Format your analysis as three clearly labeled sections. Flag any ambiguities in the problem specification.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a solution using IMPERATIVE/ITERATIVE approach:
                - Use explicit loops and indices where appropriate
                - Focus on step-by-step procedural logic
                - Include detailed comments explaining each step
                - Handle edge cases identified in decomposition: {decomposition}
                
                Return ONLY the function implementation with necessary imports, following the exact format specified in the problem.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Develop a solution using FUNCTIONAL/DECLARATIVE approach:
                - Use map/filter/reduce patterns where applicable
                - Avoid explicit loops; prefer comprehensions or recursion
                - Focus on transformation pipelines
                - Handle edge cases identified in decomposition: {decomposition}
                
                Return ONLY the function implementation with necessary imports, following the exact format specified in the problem.""",
                context=decomposition
            ),
            self.generate(
                instruction=f"""Develop a solution using MATHEMATICAL/OPTIMIZED approach:
                - Look for mathematical shortcuts or closed-form solutions
                - Consider algorithmic optimizations (O(1) vs O(n))
                - Use mathematical properties (commutativity, associativity, etc.)
                - Handle edge cases identified in decomposition: {decomposition}
                
                Return ONLY the function implementation with necessary imports, following the exact format specified in the problem.""",
                context=decomposition
            )
        ]
        
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # PHASE 3: STRATEGY ENSEMBLE & SYNTHESIS
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all provided solutions:
            - Combine robustness from imperative approach
            - Incorporate elegance from functional approach
            - Integrate efficiency from mathematical approach
            - Ensure all edge cases are handled
            - Maintain exact function signature and return type
            - Prioritize clarity and correctness over cleverness
            
            Return ONLY the final function implementation with necessary imports, following the exact format specified in the problem.""",
            contexts_list=strategy_solutions
        )

        # PHASE 4: ADVERSARIAL VALIDATION & ITERATIVE REFINEMENT
        for iteration in range(3):  # Maximum 3 refinement cycles
            validation = await self.generate(
                instruction=f"""Perform adversarial validation of the current solution:
                1. Generate 5 test cases that would likely break this solution (edge cases, boundary conditions, type mismatches)
                2. For each test case, predict the output and explain why it should be correct
                3. Identify any discrepancies between expected and actual behavior
                4. If no issues found, state "VALIDATION PASSED" with confidence level
                
                Current solution:
                {synthesized_solution}""",
                context=synthesized_solution
            )
            
            if "VALIDATION PASSED" in validation and "high confidence" in validation.lower():
                break  # Early termination if validation is confident
                
            # Revise based on validation feedback
            synthesized_solution = await self.revise(
                instruction=f"""Revise the solution to address validation issues:
                Validation feedback: {validation}
                
                Specific requirements:
                - Fix all identified issues while preserving core functionality
                - Maintain exact function signature and return type
                - Ensure backward compatibility with previously working cases
                - Add defensive checks for edge cases if needed
                - Keep code clean and readable
                
                Return ONLY the revised function implementation with necessary imports, following the exact format specified in the problem.""",
                context=synthesized_solution
            )

        # PHASE 5: FINAL CLEANUP & FORMAT ENFORCEMENT
        final_solution = await self.revise(
            instruction="""Final cleanup and format enforcement:
            - Ensure ONLY the function implementation is returned (no explanations, no markdown)
            - Verify exact function name and parameter names match specification
            - Include all necessary imports at top of function
            - Remove any debug statements or print calls
            - Ensure proper indentation and Python syntax
            - Return type must exactly match problem requirements
            
            This is the final output that will be executed - it must be pristine.""",
            context=synthesized_solution
        )

        return final_solution