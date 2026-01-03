# Workflow ID: mbppplus_82_0
# Benchmark: mbppplus
# Data Indices: [74, 336, 73]

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

        # PHASE 1: PROBLEM CLASSIFICATION & INTENT EXTRACTION
        problem_analysis = await self.generate(
            instruction="""Perform deep problem analysis. Identify:
            1. Primary computational category (mathematical, string, list, logical, etc.)
            2. Key constraints (preserve order? handle empties? specific return type?)
            3. Edge cases to consider (empty inputs, single elements, duplicates, boundaries)
            4. Expected output format and type
            5. Any hidden conditions or implicit rules
            Structure your response as a numbered list with clear, concise points.""",
            context=""
        )

        # PHASE 2: PARALLEL STRATEGY GENERATION
        strategy_tasks = [
            self.generate(
                instruction=f"""Solve using MATHEMATICAL/LOGICAL approach:
                Problem context: {problem_analysis}
                - Use algebraic reasoning, conditionals, numerical ranges
                - Handle edge cases explicitly (empty, boundaries, type mismatches)
                - Return correct data type as specified
                - Write clean, minimal code with clear variable names""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using DATA STRUCTURE approach:
                Problem context: {problem_analysis}
                - Leverage sets, counters, dictionaries, or ordered dicts as appropriate
                - Focus on efficient lookups, frequency counting, or deduplication
                - Preserve order if required, handle duplicates correctly
                - Return correct data type as specified
                - Write clean, minimal code with clear variable names""",
                context=""
            ),
            self.generate(
                instruction=f"""Solve using IMPERATIVE/PROCEDURAL approach:
                Problem context: {problem_analysis}
                - Use explicit loops, conditionals, step-by-step logic
                - Handle edge cases with explicit if-checks
                - Return correct data type as specified
                - Write clean, minimal code with clear variable names""",
                context=""
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # PHASE 3: VALIDATION & REFINEMENT
        validation_tasks = [
            self.revise(
                instruction="""Validate and refine this solution:
            1. Check type consistency (input/output types match problem)
            2. Verify edge case handling (empty inputs, single elements, duplicates, boundaries)
            3. Ensure logic matches test case patterns
            4. Fix any bugs or inconsistencies found
            5. If solution is robust, return it unchanged with comment '# VALIDATED'
            6. If flawed, fix it or return 'INVALID: [reason]'""",
                context=candidate
            ) for candidate in strategy_candidates
        ]
        
        validated_candidates = await asyncio.gather(*validation_tasks)

        # PHASE 4: ENSEMBLE SELECTION & SYNTHESIS
        final_solution = await self.ensemble(
            instruction="""Select or synthesize the best solution:
            - Prefer solutions marked '# VALIDATED'
            - If multiple valid, pick the most elegant/readable
            - If none fully valid, synthesize a hybrid using strongest parts
            - Ensure final solution handles all edge cases mentioned in analysis
            - Return ONLY the final function implementation (no explanations)
            - Must match exact function signature from problem
            - Include necessary imports at top if any""",
            contexts_list=validated_candidates
        )

        # PHASE 5: ITERATIVE VALIDATION (if needed)
        test_simulation = await self.generate(
            instruction=f"""Simulate test validation for this solution:
            Solution: {final_solution}
            Problem context: {problem_analysis}
            Generate 3 test cases including edge cases. Does solution pass?
            If any failure, explain exactly what breaks and how to fix.
            If all pass, return 'PASSES_ALL_TESTS'""",
            context=final_solution
        )

        if "PASSES_ALL_TESTS" not in test_simulation:
            final_solution = await self.revise(
                instruction=f"""Fix the solution based on test failures:
                Test feedback: {test_simulation}
                Problem context: {problem_analysis}
                Return ONLY the corrected function implementation.
                Must handle all edge cases and match exact signature.""",
                context=final_solution
            )

        return final_solution