# Workflow ID: mbppplus_15_0
# Benchmark: mbppplus
# Data Indices: [343, 172, 242]

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
        Universal workflow for algorithmic programming problems.
        Dynamically classifies problem type, generates multiple solution strategies,
        refines them, and selects the optimal implementation.
        """
        import asyncio
        import re

        # Phase 1: Problem Classification
        classification = await self.generate(
            instruction="""Analyze this programming problem in depth. Determine:
            1. Input type(s): What data types are provided? (string, list, integer, etc.)
            2. Output type: What should be returned? (int, tuple, list, etc.)
            3. Core operation: What is the fundamental task? (search, generate, transform, validate, etc.)
            4. Algorithmic pattern: What standard algorithms or techniques apply? (regex, heap, DP, iteration, etc.)
            5. Edge cases: What boundary conditions must be handled? (empty input, no matches, single elements, etc.)
            6. Constraints: Any performance, memory, or implementation restrictions?
            Structure your response clearly with these numbered headings.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_tasks = [
            self.generate(
                instruction=f"""Based on this problem classification:
                {classification}
                
                Strategy A - Direct & Built-in: Solve using Python's built-in functions and straightforward logic.
                - Use methods like str.find, re.search, list comprehensions, etc.
                - Prioritize readability and simplicity.
                - Handle all edge cases explicitly.
                - Return correct data type.
                - Include necessary imports inside function if needed.
                Output only the function implementation with exact required signature.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on this problem classification:
                {classification}
                
                Strategy B - Algorithmic & Explicit: Solve with explicit loops, generators, or data structures.
                - Implement core logic manually (e.g., iterate through string, manage heap, track state).
                - Focus on correctness and edge case handling.
                - Optimize for clarity over cleverness.
                - Return correct data type.
                - Include necessary imports inside function if needed.
                Output only the function implementation with exact required signature.""",
                context=""
            ),
            self.generate(
                instruction=f"""Based on this problem classification:
                {classification}
                
                Strategy C - Functional & Transformative: Solve using functional programming concepts or set operations.
                - Use map/filter, generators, itertools, set operations, etc.
                - Emphasize declarative style and transformation pipelines.
                - Handle edge cases gracefully.
                - Return correct data type.
                - Include necessary imports inside function if needed.
                Output only the function implementation with exact required signature.""",
                context=""
            )
        ]
        
        strategy_candidates = await asyncio.gather(*strategy_tasks)

        # Phase 3: Parallel Strategy Refinement
        refinement_tasks = [
            self.revise(
                instruction="""Critically evaluate this solution:
                1. Is the logic correct for all cases including edge cases?
                2. Does it return the exact required data type?
                3. Are imports properly placed (inside function if needed)?
                4. Is it efficient and avoid unnecessary complexity?
                5. Does it follow Python best practices?
                If any issues are found, revise the code to fix them. If fundamentally flawed, rewrite using better approach.
                Output only the corrected function implementation.""",
                context=candidate
            ) for candidate in strategy_candidates
        ]
        
        refined_candidates = await asyncio.gather(*refinement_tasks)

        # Phase 4: Ensemble Selection
        final_solution = await self.ensemble(
            instruction="""You are given multiple candidate solutions to the same programming problem.
            Evaluate each for:
            1. Correctness: Does it handle all edge cases and produce right output?
            2. Efficiency: Is it reasonably performant for expected inputs?
            3. Clarity: Is the code readable and maintainable?
            4. Robustness: Does it handle unexpected inputs gracefully?
            5. Format: Does it match required output format exactly?
            Select the single best solution. If multiple are equally good, choose the simplest.
            If you can create a better solution by combining elements from multiple candidates, do so.
            Output only the final function implementation with exact required signature and necessary imports inside function.""",
            contexts_list=refined_candidates
        )

        # Phase 5: Final Formatting Enforcement
        final_code = await self.revise(
            instruction="""Format this code EXACTLY according to requirements:
            1. Output ONLY the function implementation - no explanations, no markdown.
            2. Use the EXACT function name and parameters from the problem.
            3. Place ALL imports inside the function if needed.
            4. Ensure return type matches expected output exactly.
            5. Remove any extra text, comments, or formatting.
            6. Code must be ready to execute as-is.
            Output only the raw code block with no additional text.""",
            context=final_solution
        )

        return final_code