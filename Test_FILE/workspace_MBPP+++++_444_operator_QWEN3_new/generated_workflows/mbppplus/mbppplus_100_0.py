# Workflow ID: mbppplus_100_0
# Benchmark: mbppplus
# Data Indices: [354, 199, 308]

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

    async def run_workflow(self):
        import asyncio
        import re

        # Stage 1: Problem Classification & Requirement Extraction
        classification = await self.generate(
            instruction="""Analyze this programming problem with extreme precision. Classify it by:
            1. Primary domain (number theory, string manipulation, data structure, logic, etc.)
            2. Input type and constraints (int, str, list, etc. + edge cases like empty, zero, negatives)
            3. Output type and format requirements (bool, int, str, list, tuple, etc.)
            4. Algorithmic pattern (search, filter, transform, validate, generate, etc.)
            5. Critical edge cases to handle (extract from problem description and infer common ones)
            Format as a structured JSON-like block with clear section headers.""",
            context=""
        )

        # Stage 2: Parallel Solution Generation
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function solution based on this classification:
                {classification}
                
                Requirements:
                - Use EXACT function signature from problem
                - Handle ALL edge cases mentioned in classification
                - Prioritize readability and correctness over cleverness
                - Include necessary imports inside function if needed
                - Return correct data type as specified
                - NO wrapper functions or classes
                Output ONLY the function code, nothing else.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate an ALTERNATIVE Python solution using a different algorithmic approach:
                Classification: {classification}
                
                Requirements:
                - Must use fundamentally different logic (e.g., if first used loops, use comprehensions or built-ins)
                - Still handle all edge cases
                - Focus on efficiency or simplicity as contrast to first solution
                - Same strict output format requirements
                Output ONLY the function code.""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a DEFENSIVE Python solution that prioritizes robustness:
                Classification: {classification}
                
                Requirements:
                - Include explicit edge case handling with conditionals
                - Add input validation if appropriate
                - Use verbose but foolproof logic
                - Same signature and return type constraints
                - Comment edge case handling clearly
                Output ONLY the function code.""",
                context=""
            )
        )

        # Stage 3: Parallel Edge Case Critique
        critiques = await asyncio.gather(
            *[self.revise(
                instruction=f"""CRITIQUE this solution for edge cases and conformance:
                Classification context: {classification}
                
                Perform adversarial validation:
                1. What edge cases from classification are NOT handled?
                2. Does it match required return type exactly?
                3. Are there type coercion issues?
                4. Off-by-one errors? Infinite loops? Division by zero?
                5. Does it handle empty inputs, single elements, extremes?
                6. Is the function signature preserved exactly?
                Provide SPECIFIC line-by-line feedback with concrete fixes needed.""",
                context=solution
            ) for solution in solution_attempts]
        )

        # Stage 4: Parallel Solution Revision
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""REVISE this solution based on critique:
                Critique: {critique}
                
                Requirements:
                - Fix ALL identified issues
                - Preserve original algorithmic approach unless fundamentally flawed
                - Maintain exact function signature
                - Ensure return type matches specification
                - Add minimal necessary edge case handling
                Output ONLY the corrected function code.""",
                context=solution
            ) for solution, critique in zip(solution_attempts, critiques)]
        )

        # Stage 5: Ensemble Selection with Conformance Check
        final_selection = await self.ensemble(
            instruction=f"""SELECT the BEST solution from these candidates:
            Classification: {classification}
            
            Selection criteria:
            1. Correctness (handles all edge cases from classification)
            2. Conformance (exact signature, return type, no extra output)
            3. Readability and maintainability
            4. Efficiency (avoid unnecessary complexity)
            5. Robustness (defensive programming where needed)
            
            If no single solution is perfect, SYNTHESIZE a hybrid by combining strongest elements.
            Output ONLY the final function code, nothing else.""",
            contexts_list=revised_solutions
        )

        # Stage 6: Final Conformance Verification & Cleanup
        final_code = await self.revise(
            instruction="""FINAL SANITY CHECK:
            1. Does this code have EXACTLY the function signature required?
            2. Are all imports inside the function or at top of file as needed?
            3. Does it return correct data type (bool/int/str/list/tuple)?
            4. Is there any extra output, print statements, or wrapper code?
            5. Are edge cases explicitly handled?
            
            If any issue found, fix it. Otherwise, return code unchanged.
            Output ONLY the function code, nothing else.""",
            context=final_selection
        )

        return final_code