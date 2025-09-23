# Workflow ID: humaneval_24_0
# Benchmark: humaneval
# Data Indices: [62, 57]

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
        Universal code generation workflow for specification-driven function implementation.
        Handles mathematical, logical, and algorithmic problems by analyzing examples,
        generating multiple candidates, validating against constraints, and selecting
        the optimal solution.
        """
        import asyncio
        import re

        # STEP 1: ANALYZE PROBLEM STRUCTURE & EXTRACT PATTERNS
        analysis = await self.generate(
            instruction="""Thoroughly analyze the problem specification and examples to extract:
            1. Core transformation or logical rule being implemented
            2. All demonstrated edge cases (empty inputs, single elements, zeros, etc.)
            3. Expected input/output types and structures
            4. Problem category (mathematical, logical, string, list processing, etc.)
            5. Any constraints or invariants that must be preserved
            6. Return type requirements (int vs float, list structure, etc.)
            7. Function naming requirement from ENTRY POINT
            Present findings in structured format with clear section headers.
            Focus on what MUST be implemented, not what could be added.""",
            context=""
        )

        # STEP 2: GENERATE MULTIPLE CANDIDATE SOLUTIONS IN PARALLEL
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate Python code implementing the specified function.
                Problem Analysis: {analysis}
                
                Strategy 1: Direct Pattern Implementation
                - Implement the most straightforward interpretation of the examples
                - Use minimal, clear logic that directly maps inputs to outputs
                - Handle all edge cases identified in analysis
                - Match return types exactly as shown in examples
                - Function name must match ENTRY POINT exactly
                - No imports unless absolutely necessary (add inside function if needed)
                - No extra features or optimizations beyond specification""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Python code implementing the specified function.
                Problem Analysis: {analysis}
                
                Strategy 2: Algorithmic/Formula-Based Approach
                - Look for mathematical formulas or algorithmic patterns
                - Use list comprehensions, enumerations, or mathematical operations where appropriate
                - Handle edge cases explicitly
                - Ensure return types match examples precisely
                - Function name must match ENTRY POINT exactly
                - Avoid unnecessary complexity
                - Include comments only if they clarify non-obvious logic""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate Python code implementing the specified function.
                Problem Analysis: {analysis}
                
                Strategy 3: Iterative/Step-by-Step Approach
                - Implement using explicit loops and conditionals
                - Build result step by step, mirroring example transformations
                - Handle edge cases with dedicated conditions
                - Match return types exactly
                - Function name must match ENTRY POINT exactly
                - Prioritize clarity and direct correspondence to examples
                - Avoid clever one-liners if they obscure logic""",
                context=""
            )
        ]
        
        # Execute parallel generation
        candidates = await asyncio.gather(*candidate_tasks)

        # STEP 3: VALIDATE AND REVISE EACH CANDIDATE
        validation_tasks = []
        for i, candidate in enumerate(candidates):
            validation = await self.generate(
                instruction=f"""Critically validate this candidate solution against the problem specification:
                Problem Analysis: {analysis}
                Candidate Code: {candidate}
                
                Check for:
                1. Correct function name matching ENTRY POINT exactly
                2. Handling of all edge cases identified in analysis
                3. Return type matches (int vs float, list structure, etc.)
                4. Logic correctly implements demonstrated examples
                5. No over-engineering or extra features
                6. Code is minimal and focused on specification
                
                If any issues found, provide specific, actionable feedback.
                If no issues, state "VALID: Ready for selection".
                Format feedback as bullet points with clear error descriptions.""",
                context=candidate
            )
            
            # Revise if validation found issues
            if "VALID:" not in validation:
                revised = await self.revise(
                    instruction=f"""Revise the code to fix all issues identified in validation:
                    Validation Feedback: {validation}
                    Problem Analysis: {analysis}
                    
                    Requirements:
                    - Fix all identified issues while preserving correct functionality
                    - Maintain exact function name from ENTRY POINT
                    - Ensure return types match examples precisely
                    - Handle all edge cases
                    - Keep code minimal and focused
                    - Do not introduce new issues or complexity""",
                    context=candidate
                )
                validation_tasks.append(revised)
            else:
                validation_tasks.append(candidate)

        validated_candidates = await asyncio.gather(*[asyncio.create_task(self.generate(instruction="Return as-is", context=c)) for c in validation_tasks])

        # STEP 4: ENSEMBLE SELECTION - CHOOSE BEST CANDIDATE
        final_selection = await self.ensemble(
            instruction="""Select the best candidate solution based on:
            1. Correctness: Must handle all edge cases and match examples
            2. Simplicity: Minimal, clear code without unnecessary complexity
            3. Precision: Exact return types, correct function name
            4. Robustness: No obvious failure modes or edge case misses
            5. Directness: Closest match to specification without over-engineering
            
            If multiple candidates are equally good, prefer the one with:
            - Fewest lines of code
            - Most direct implementation of examples
            - Clearest correspondence to problem analysis
            
            Return ONLY the selected code, nothing else.""",
            contexts_list=validated_candidates
        )

        # STEP 5: FINAL POLISH - ENSURE PERFECT FORMAT
        final_code = await self.revise(
            instruction="""Final polish for submission:
            1. Ensure function name matches ENTRY POINT exactly
            2. Remove any unnecessary comments or whitespace
            3. Verify return types match examples precisely
            4. Ensure no imports are outside the function (if any needed, must be inside function)
            5. Code must be self-contained and ready for testing
            6. No markdown, no explanations, just pure Python code
            7. If function needs imports, add them inside the function body
            Return ONLY the final code, nothing else.""",
            context=final_selection
        )

        return final_code