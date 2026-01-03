# Workflow ID: mbppplus_81_0
# Benchmark: mbppplus
# Data Indices: [132, 143, 54]

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

        # Step 1: Classify and decompose the problem
        problem_classification = await self.generate(
            instruction="""Perform a deep structural analysis of this programming problem. Identify:
            1. Primary data types involved (list, tuple, set, string, number, etc.)
            2. Core operation required (search, filter, transform, validate, compute, etc.)
            3. Key constraints (sorted input? unique elements? mutability? time complexity?)
            4. Edge cases to consider (empty inputs, single elements, None values, negatives, duplicates)
            5. Expected return type and format (must match exactly: list vs tuple vs int vs bool)
            6. Algorithmic patterns that may apply (binary search, iteration, recursion, formula, etc.)
            7. Any implicit requirements from the problem context
            Present this as a structured, detailed report. This will guide all subsequent solution strategies.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategy_tasks = [
            self.generate(
                instruction=f"""Develop a BRUTE-FORCE / DIRECT implementation strategy.
                Context: {problem_classification}
                
                Guidelines:
                - Prioritize clarity and explicit handling of edge cases
                - Use simple loops and conditionals
                - Document how each edge case is handled
                - Ensure return type matches specification exactly
                - Include inline comments explaining key decisions
                - Do NOT optimize prematurely — correctness first""",
                context=problem_classification
            ),
            self.generate(
                instruction=f"""Develop an OPTIMIZED / ALGORITHMIC implementation strategy.
                Context: {problem_classification}
                
                Guidelines:
                - Leverage efficient algorithms (binary search, mathematical formulas, etc.)
                - Consider time/space complexity trade-offs
                - Handle edge cases without sacrificing efficiency
                - Use appropriate data structures for performance
                - Include complexity analysis in comments
                - Ensure return type matches specification exactly""",
                context=problem_classification
            ),
            self.generate(
                instruction=f"""Develop a PYTHONIC / FUNCTIONAL implementation strategy.
                Context: {problem_classification}
                
                Guidelines:
                - Use built-in functions, comprehensions, and functional constructs
                - Prioritize readability and idiomatic Python
                - Handle edge cases elegantly (e.g., using any(), all(), next() with defaults)
                - Avoid unnecessary loops when built-ins suffice
                - Ensure return type matches specification exactly
                - Include comments explaining Pythonic choices""",
                context=problem_classification
            )
        ]
        
        strategy_solutions = await asyncio.gather(*strategy_tasks)

        # Step 3: Ensemble synthesis - merge the best of all approaches
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all three solution strategies into one optimal implementation.
            Evaluation criteria:
            1. CORRECTNESS: Must handle all edge cases identified in classification
            2. EFFICIENCY: Prefer optimal time/space complexity without sacrificing correctness
            3. READABILITY: Code should be clear, well-commented, and Pythonic
            4. TYPE SAFETY: Return type must match specification exactly
            5. ROBUSTNESS: Should gracefully handle unexpected inputs (within problem constraints)
            
            Merge approach:
            - Take edge-case handling from brute-force if most comprehensive
            - Take algorithmic efficiency from optimized version if applicable
            - Take elegance and brevity from Pythonic version where possible
            - Resolve conflicts by prioritizing correctness > efficiency > readability
            - Add explanatory comments for non-obvious decisions
            
            Output ONLY the final function implementation with imports if needed.""",
            contexts_list=strategy_solutions
        )

        # Step 4: Adversarial revision loop (up to 2 iterations)
        current_solution = synthesized_solution
        for iteration in range(2):
            validation_feedback = await self.revise(
                instruction=f"""CRITICALLY REVIEW this code as if you were trying to BREAK it.
                Assume it contains subtle bugs. Specifically check for:
                - Off-by-one errors in loops or indices
                - Type mismatches (returning list when tuple expected, etc.)
                - Unhandled edge cases (empty inputs, None values, single elements, duplicates)
                - Boundary condition failures (min/max values, zero, negative numbers)
                - Logic errors in conditionals or loops
                - Incorrect return values for specified test cases
                - Violations of problem constraints
                
                If ANY issues are found:
                1. Describe the bug precisely
                2. Explain how to fix it
                3. Output the FULL corrected code with fixes applied
                
                If no issues found, return the original code unchanged.
                
                Current code:
                {current_solution}""",
                context=current_solution
            )
            
            # Only update if changes were made (simple heuristic: significant difference)
            if validation_feedback.strip() != current_solution.strip() and len(validation_feedback) > 10:
                current_solution = validation_feedback
            else:
                break  # No changes needed, exit early

        # Step 5: Final type and format enforcement
        final_solution = await self.revise(
            instruction=f"""FINAL SANITY CHECK: Ensure strict adherence to return type and format.
            Context: {problem_classification}
            
            Verify:
            1. Function signature matches exactly (parameter names, order)
            2. Return type is precisely as required (int, bool, list, tuple, etc.)
            3. No unnecessary imports or code outside function
            4. Code is self-contained and will run as-is
            5. All edge cases from classification are still handled
            
            If any discrepancies found, fix them and return the corrected code.
            Otherwise, return the code unchanged.
            
            Current code:
            {current_solution}""",
            context=current_solution
        )

        return final_solution