# Workflow ID: mbppplus_50_0
# Benchmark: mbppplus
# Data Indices: [298, 331, 316]

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
        import json

        # Phase 1: Problem Decomposition & Strategy Selection
        decomposition = await self.generate(
            instruction="""Perform deep problem decomposition:
            1. Identify the core operation: Is this about filtering, transformation, validation, or state tracking?
            2. Extract key constraints: What must be preserved? (order, type, duplicates, etc.)
            3. Detect implied algorithms: Does the reference solution hint at loops, recursion, regex, or set operations?
            4. Identify edge cases: What extreme inputs might break a naive solution? (empty, single element, all same, etc.)
            5. Determine return type: Must match exactly what's shown in test cases (list vs tuple vs string).
            Output as structured JSON with keys: "operation_type", "constraints", "suggested_approaches", "edge_cases", "return_type"
            """,
            context=""
        )

        # Phase 2: Parallel Solution Generation
        solution_approaches = [
            "Generate a solution that closely mirrors the reference solution's structure and logic. Preserve variable names and control flow patterns if they exist.",
            "Generate a solution using functional programming paradigms (map/filter/reduce) or built-in Python methods. Prioritize readability and conciseness.",
            "Generate a solution that aggressively handles edge cases first (empty inputs, single elements, etc.) before main logic. Use guard clauses and explicit type checks.",
            "Generate a solution optimized for performance with minimal memory usage, even if less readable. Consider generators, sets, or early termination."
        ]

        candidate_solutions = await asyncio.gather(
            *[self.generate(
                instruction=f"""Generate a complete, runnable Python function based on this approach:
                {approach}
                
                Context from problem decomposition:
                {decomposition}
                
                CRITICAL REQUIREMENTS:
                - Use EXACT function signature from problem
                - Include necessary imports inside function if needed
                - Handle ALL edge cases mentioned in decomposition
                - Return EXACT data type shown in test cases
                - No wrapper functions or classes
                """,
                context=decomposition
            ) for approach in solution_approaches]
        )

        # Phase 3: Solution Synthesis & Refinement
        synthesized_solution = await self.ensemble(
            instruction="""Synthesize the best elements from all candidate solutions:
            1. Select the solution with the most robust edge case handling
            2. Incorporate performance optimizations from other candidates if they don't compromise correctness
            3. Ensure variable names and structure are clear and Pythonic
            4. Verify that imports are correctly placed and minimal
            5. Confirm return type matches test cases exactly
            6. Add inline comments ONLY if they clarify non-obvious logic
            Output ONLY the final function implementation with imports, nothing else.
            """,
            contexts_list=candidate_solutions
        )

        # Phase 4: Validation & Iterative Refinement (up to 3 attempts)
        current_solution = synthesized_solution
        for iteration in range(3):
            validation_feedback = await self.generate(
                instruction=f"""Rigorously validate this solution:
                {current_solution}
                
                Based on problem decomposition:
                {decomposition}
                
                CHECKLIST:
                1. Does it handle all edge cases from decomposition?
                2. Does it preserve required order/type/structure?
                3. Are there any off-by-one errors or boundary condition failures?
                4. Is the return type exactly as specified?
                5. Are imports correctly placed and necessary?
                6. Does it match the reference solution's intent without copying?
                
                If any issues found, describe them SPECIFICALLY. If perfect, say "VALIDATED".
                """,
                context=current_solution
            )

            if "VALIDATED" in validation_feedback:
                break
                
            # Revise based on specific feedback
            current_solution = await self.revise(
                instruction=f"""Revise the solution to fix these specific issues:
                {validation_feedback}
                
                Additional requirements:
                - Maintain exact function signature
                - Preserve all previously working functionality
                - Add explicit handling for any missing edge cases
                - Keep code as concise as possible while being robust
                - Return ONLY the complete function implementation
                """,
                context=current_solution
            )
        else:
            # If we exhausted iterations, use last revision
            pass

        return current_solution