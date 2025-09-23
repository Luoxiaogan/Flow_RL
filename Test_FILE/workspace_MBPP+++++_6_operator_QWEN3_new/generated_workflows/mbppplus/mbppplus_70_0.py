# Workflow ID: mbppplus_70_0
# Benchmark: mbppplus
# Data Indices: [150, 305]

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

        # Step 1: Decompose the problem into its core components
        decomposition = await self.decompose(
            instruction="""Break down this programming problem into fundamental components:
            1. Input type and structure (list, string, tuple, etc.)
            2. Output type and structure (boolean, list of tuples, etc.)
            3. Core operation (validation, extraction, transformation, calculation)
            4. Key constraints or edge cases (empty inputs, boundary conditions)
            5. Suggested algorithmic approaches (recursive, iterative, regex, etc.)
            6. Complexity category (simple, moderate, complex)
            Return as structured list of subproblems with clear descriptions.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategy_tasks = []
        for i in range(3):  # Generate 3 different approaches
            strategy_tasks.append(
                self.generate(
                    instruction=f"""Propose a complete solution strategy for this problem:
                    - Based on decomposition: {json.dumps(decomposition)}
                    - Approach {i+1}: Consider a different paradigm (recursive, iterative, functional, regex-based, etc.)
                    - Include handling of edge cases identified in decomposition
                    - Specify exact function signature and return type
                    - Outline step-by-step logic with key considerations
                    Be detailed and technically precise.""",
                    context=""
                )
            )
        
        strategies = await asyncio.gather(*strategy_tasks)

        # Step 3: Generate code implementations for each strategy
        code_tasks = []
        for i, strategy in enumerate(strategies):
            code_tasks.append(
                self.programmer(
                    instruction=f"""Implement the following solution strategy:
                    Strategy: {strategy}
                    
                    Requirements:
                    - Use EXACT function name and signature from problem
                    - Handle all edge cases mentioned in decomposition
                    - Include type hints if applicable
                    - Add brief comments explaining key logic
                    - Return correct data type (list, tuple, boolean, etc.)
                    - Import any needed modules inside function if necessary
                    
                    Generate clean, production-ready Python code.""",
                    context=strategy
                )
            )
        
        code_results = await asyncio.gather(*code_tasks)

        # Step 4: Ensemble - Synthesize best elements from all implementations
        synthesized_code = await self.ensemble(
            instruction="""Synthesize the best implementation from these candidates:
            - Compare for correctness, edge case handling, and code quality
            - Prefer solutions that explicitly handle edge cases
            - Combine strongest elements if no single solution is perfect
            - Ensure function signature matches exactly
            - Output ONLY the final Python code with imports and function definition
            - No explanations or markdown - just raw code""",
            contexts_list=code_results
        )

        # Step 5: Iterative refinement loop (up to 3 attempts)
        current_code = synthesized_code
        for attempt in range(3):
            # Test the code (programmer operator will execute and catch errors)
            test_result = await self.programmer(
                instruction="""Test this implementation with comprehensive test cases including edge cases.
                If errors occur, return detailed error description.
                If successful, return 'SUCCESS'.
                Focus on: type mismatches, index errors, logic flaws, empty input handling.""",
                context=current_code
            )
            
            if "SUCCESS" in test_result:
                break
            else:
                # Revise based on error
                current_code = await self.revise(
                    instruction=f"""Fix the implementation based on this error:
                    Error: {test_result}
                    
                    Requirements:
                    - Preserve working parts of the code
                    - Fix only the identified issues
                    - Maintain exact function signature
                    - Improve edge case handling if needed
                    - Return complete corrected code""",
                    context=current_code
                )
        else:
            # If all revisions failed, attempt meta-revision
            current_code = await self.generate(
                instruction=f"""Re-approach this problem from first principles:
                Previous attempts failed with: {test_result}
                Consider completely different algorithmic paradigms.
                Generate a fresh implementation that avoids previous pitfalls.
                Focus on robustness and edge case handling.
                Return complete Python code with exact function signature.""",
                context=current_code
            )

        # Step 6: Final cleanup and standardization
        final_code = await self.revise(
            instruction="""Finalize this code for production:
            - Ensure exact function name and signature as specified
            - Remove any debug prints or unnecessary comments
            - Standardize formatting (PEP8)
            - Verify all edge cases are handled
            - Return ONLY the raw Python code - no markdown, no explanations
            - Include necessary imports at top of function if needed""",
            context=current_code
        )

        return final_code