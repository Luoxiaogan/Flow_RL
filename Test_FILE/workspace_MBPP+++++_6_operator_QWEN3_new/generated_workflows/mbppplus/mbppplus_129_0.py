# Workflow ID: mbppplus_129_0
# Benchmark: mbppplus
# Data Indices: [118, 140]

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

        # Step 1: Classify the problem type and extract key constraints
        classification = await self.generate(
            instruction="""Analyze the problem and classify it into one of these categories:
            - String Pattern Matching (regex, substring, wildcards)
            - Character Uniformity Check (all same/different characters)
            - List/Tuple Operations (filtering, transformations, set operations)
            - Mathematical Computation (number theory, sequences, arithmetic)
            - Logic/Validation (conditional processing, comparisons, boolean logic)
            
            Also extract:
            - Expected input types and structures
            - Required return type (list, tuple, string, boolean, etc.)
            - Key edge cases to handle (empty inputs, single elements, duplicates, boundaries)
            - Any explicit or implicit constraints mentioned
            
            Format your response as a structured JSON-like summary with clear labels.""",
            context=""
        )

        # Step 2: Generate initial solution strategy based on classification
        strategy = await self.generate(
            instruction=f"""Based on this classification:
            {classification}
            
            Design a precise implementation strategy:
            - Specify exact algorithm or approach to use
            - Detail how to handle identified edge cases
            - Enforce correct return type and function signature
            - Include any necessary imports (re, math, etc.)
            - Mention any Python built-ins or standard library functions to leverage
            - Emphasize defensive programming for robustness
            
            Output only the implementation plan, no code yet.""",
            context=classification
        )

        # Step 3: Generate initial code implementation
        initial_code = await self.programmer(
            instruction=f"""Implement the solution according to this strategy:
            {strategy}
            
            Critical requirements:
            - Use EXACT function name and parameters from problem
            - Return correct data type (match test case return types exactly)
            - Handle ALL edge cases mentioned in classification
            - Include necessary imports inside function if needed
            - Write clean, efficient, readable code
            - No wrapper functions or classes - only the requested function
            - If regex is involved, use 're' module appropriately
            - For string problems, consider encoding/empty string edge cases
            - For numeric problems, consider negative/zero/overflow cases""",
            context=strategy,
            max_retries=2
        )

        # Step 4: Parallel revision tracks - Edge Case Robustness + Type/Signature Compliance
        robustness_revision = await self.revise(
            instruction="""Critically examine this code for edge case handling:
            - Does it handle empty inputs correctly?
            - Does it handle single-element cases?
            - Are boundary conditions properly managed?
            - Are there any unhandled type variations?
            - Could duplicates or special values cause issues?
            - Is there any potential for index errors or division by zero?
            
            Improve the code to make it maximally robust. Preserve function signature and core logic.
            Return only the improved code.""",
            context=initial_code
        )

        type_revision = await self.revise(
            instruction="""Critically examine this code for type and signature compliance:
            - Does it use the EXACT function name specified?
            - Do parameter names match exactly?
            - Does return type match what's shown in test cases (tuple vs list vs string)?
            - Are imports correctly placed and necessary?
            - Is the code structured exactly as required (no outer wrappers)?
            - Does it avoid common pitfalls like mixing data types?
            
            Improve the code to ensure perfect compliance. Preserve core logic.
            Return only the improved code.""",
            context=initial_code
        )

        # Step 5: Ensemble - Merge the best of both revisions
        final_code = await self.ensemble(
            instruction="""You have two revised versions of the same code:
            Version A: Focused on edge case robustness
            Version B: Focused on type/signature compliance
            
            Synthesize them into a single optimal solution that:
            - Incorporates all robustness improvements from Version A
            - Maintains perfect type/signature compliance from Version B
            - Is clean, efficient, and readable
            - Handles all edge cases while preserving exact function signature
            - Returns only the final code with no additional text or explanation""",
            contexts_list=[robustness_revision, type_revision]
        )

        # Step 6: Validation and adaptive refinement loop (max 2 iterations)
        for attempt in range(2):
            validation = await self.generate(
                instruction=f"""Validate this code against the original problem:
                {final_code}
                
                Check for:
                - Logical correctness (does it solve what's asked?)
                - Signature compliance (exact function name, parameters, return type)
                - Edge case coverage (empty, single, boundary, duplicates)
                - Potential runtime errors (index out of bounds, type errors, etc.)
                - Efficiency concerns (unnecessary loops, redundant operations)
                
                If any issues found, describe them specifically. If perfect, say "VALIDATED".
                Be brutally honest - this code will face hundreds of test cases.""",
                context=final_code
            )

            if "VALIDATED" in validation.upper() and "ISSUE" not in validation.upper() and "ERROR" not in validation.upper():
                break
                
            # If issues found, revise and continue
            final_code = await self.revise(
                instruction=f"""Fix all issues identified in this validation:
                {validation}
                
                Specific requirements:
                - Maintain exact function signature
                - Preserve all previous robustness and compliance improvements
                - Address every single issue mentioned
                - Return only the corrected code with no additional text""",
                context=final_code
            )
        else:
            # Final fallback: if still not validated, return best effort with warning comment
            final_code = "# WARNING: Auto-generated solution - may require manual review\n" + final_code

        return final_code