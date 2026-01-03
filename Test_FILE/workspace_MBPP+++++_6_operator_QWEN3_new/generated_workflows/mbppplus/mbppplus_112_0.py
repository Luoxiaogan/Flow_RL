# Workflow ID: mbppplus_112_0
# Benchmark: mbppplus
# Data Indices: [334, 364]

import asyncio

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
        import json

        # Step 1: Decompose the problem into core components
        decomposition = await self.decompose(
            instruction="""Break this programming problem into essential subproblems:
            1. What is the exact functional requirement? (input → output mapping)
            2. What are the data types involved? (list, tuple, string, int, etc.)
            3. What edge cases must be handled? (empty, single element, duplicates, boundaries)
            4. What algorithmic approach is most suitable? (mathematical, iterative, regex, etc.)
            5. What are the performance or efficiency constraints?
            Return structured subproblems with clear dependencies.""",
            context=""
        )

        # Step 2: Parallel generation of solution perspectives
        perspectives = await asyncio.gather(
            self.generate(
                instruction="""Adopt a MATHEMATICAL/FORMULAIC perspective:
                - Derive closed-form solutions if applicable
                - Use algebraic reasoning
                - Optimize for O(1) time if possible
                - Show step-by-step derivation
                - Handle integer/float boundaries""",
                context=json.dumps(decomposition)
            ),
            self.generate(
                instruction="""Adopt a STRING/DATA STRUCTURE perspective:
                - Focus on pattern matching, parsing, transformations
                - Consider regex, slicing, iteration
                - Handle case sensitivity, whitespace, encoding
                - Preserve order and type requirements
                - Optimize for readability and maintainability""",
                context=json.dumps(decomposition)
            ),
            self.generate(
                instruction="""Adopt an EDGE CASE & ROBUSTNESS perspective:
                - Enumerate all possible edge cases: empty, null, single, max, min, duplicates
                - Consider type coercion, overflow, precision loss
                - Design defensive checks and fallbacks
                - Ensure type consistency in returns
                - Validate against implicit constraints""",
                context=json.dumps(decomposition)
            )
        )

        # Step 3: Generate candidate code implementations from each perspective
        code_candidates = await asyncio.gather(
            *[self.programmer(
                instruction=f"""Generate a complete, runnable Python function based on this perspective:
                {perspective}
                
                Requirements:
                - Match the exact function signature from the problem
                - Include necessary imports inside the function if needed
                - Handle all edge cases identified in decomposition
                - Return correct data type (list/tuple/set/string/int)
                - No print statements, only return values
                - Must be self-contained and immediately executable""",
                context=perspective,
                max_retries=1
            ) for perspective in perspectives]
        )

        # Step 4: Ensemble select the best candidate based on correctness and robustness
        best_code = await self.ensemble(
            instruction="""Select the BEST code implementation based on:
            1. Correctness: Matches expected behavior for all test cases
            2. Robustness: Handles edge cases comprehensively
            3. Type Safety: Returns correct data type
            4. Efficiency: Optimal time/space complexity
            5. Readability: Clean, well-structured code
            6. Adherence: Matches function signature exactly
            
            If multiple candidates are strong, synthesize a hybrid solution.
            Prioritize correctness and edge case handling above all else.""",
            contexts_list=code_candidates
        )

        # Step 5: Iterative validation and revision loop
        current_code = best_code
        for iteration in range(3):  # Max 3 revision cycles
            validation_result = await self.programmer(
                instruction=f"""Test this code against edge cases:
                {current_code}
                
                Generate 5 test cases including:
                - Normal case
                - Empty input
                - Boundary values
                - Type edge cases
                - Performance stress test
                
                Return ONLY in JSON format: {{"passed": true/false, "errors": ["list of errors"], "suggested_fixes": ["list of fixes"]}}""",
                context=current_code,
                max_retries=1
            )

            try:
                validation_json = json.loads(validation_result)
                if validation_json.get("passed", False):
                    break  # Exit loop if all tests pass
                else:
                    # Revise based on specific errors
                    current_code = await self.revise(
                        instruction=f"""Fix these specific issues:
                        Errors: {validation_json.get('errors', [])}
                        Suggested Fixes: {validation_json.get('suggested_fixes', [])}
                        
                        Requirements:
                        - Maintain exact function signature
                        - Preserve data types
                        - Handle all edge cases
                        - No new bugs introduced
                        - Code must be production-ready""",
                        context=current_code
                    )
            except:
                # If validation fails to parse, do one generic revision
                current_code = await self.revise(
                    instruction="""Improve robustness and fix potential edge case failures.
                    Ensure type safety and handle empty/null inputs.
                    Match function signature exactly.
                    Return appropriate data type.""",
                    context=current_code
                )

        # Step 6: Final cleanup and standardization
        final_code = await self.revise(
            instruction="""Finalize code for production:
            - Remove any debug statements or comments
            - Ensure PEP8 compliance
            - Verify function signature matches exactly
            - Confirm return type is correct
            - Optimize for clarity and efficiency
            - No external dependencies unless absolutely necessary
            - Must be copy-paste runnable""",
            context=current_code
        )

        return final_code