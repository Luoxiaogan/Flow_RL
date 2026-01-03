# Workflow ID: humaneval_3_0
# Benchmark: humaneval
# Data Indices: [46, 63]

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
        Universal workflow for generating Python functions from specifications.
        Uses parallel solution generation, validation, and synthesis.
        """
        import asyncio
        import re

        # Step 1: Decompose the problem into structured components
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the problem specification and extract the following in a structured format:
            1. Function signature: Exact name and parameters
            2. Base cases: All explicitly stated base cases from examples (e.g., f(0)=0, f(1)=1)
            3. Recurrence/Transformation rule: The general rule for computing f(n) from previous values or inputs
            4. Constraints: Any explicit restrictions (e.g., "do not use recursion", "use O(1) space")
            5. Return type: Must be inferred from examples (int, float, str, list, etc.)
            6. Edge cases: Infer additional edge cases not explicitly stated (e.g., negative inputs, very large n)
            7. Problem category: Classify as one of: [fibonacci-like, string-manipulation, mathematical-formula, list-processing, other]
            
            Format your response as a JSON-like structure with clear section headers.
            """,
            context=""
        )

        # Step 2: Generate multiple solution candidates in parallel
        candidate_tasks = [
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following strategy:
                Strategy: Recursive implementation (only if not forbidden by constraints)
                Use the problem decomposition: {decomposition}
                - Implement base cases exactly as specified
                - Follow the recurrence rule precisely
                - Ensure return type matches examples
                - Include no extra functionality
                Return ONLY the function code, no explanations.
                """,
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following strategy:
                Strategy: Iterative implementation with dynamic programming (sliding window if space constrained)
                Use the problem decomposition: {decomposition}
                - Precompute base cases
                - Iterate from smallest to target value
                - Optimize for space if constraint mentions it
                - Ensure return type matches examples
                Return ONLY the function code, no explanations.
                """,
                context=decomposition
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation based on the following strategy:
                Strategy: Mathematical closed-form or optimized formula (if applicable)
                Use the problem decomposition: {decomposition}
                - Only use if the recurrence suggests a pattern that can be simplified
                - Otherwise, fall back to iterative
                - Ensure return type matches examples
                Return ONLY the function code, no explanations.
                """,
                context=decomposition
            )
        ]
        
        candidates = await asyncio.gather(*candidate_tasks)

        # Step 3: Validate each candidate against visible examples and revise if needed
        validated_candidates = []
        for i, candidate in enumerate(candidates):
            # First validation: check against docstring examples
            validation = await self.generate(
                instruction=f"""Validate this candidate code against the problem specification:
                Candidate Code:
                {candidate}
                
                Problem Decomposition:
                {decomposition}
                
                Check for:
                1. Correct function name and signature
                2. All base cases handled
                3. Correct recurrence/transformation implementation
                4. Return type matches examples
                5. No violation of constraints (e.g., no recursion if forbidden)
                6. Passes all examples in docstring
                
                If any issues, list them specifically. If perfect, say "VALID".
                """,
                context=candidate
            )
            
            # Revise if issues found
            if "VALID" not in validation.upper():
                revised_candidate = await self.revise(
                    instruction=f"""Fix the following issues in the candidate code:
                    Issues: {validation}
                    
                    Original candidate:
                    {candidate}
                    
                    Problem decomposition for reference:
                    {decomposition}
                    
                    Return ONLY the corrected function code.
                    """,
                    context=candidate
                )
                validated_candidates.append(revised_candidate)
            else:
                validated_candidates.append(candidate)

        # Step 4: Ensemble - select the best candidate
        final_code = await self.ensemble(
            instruction="""Select the best implementation from the candidates below based on:
            1. Correctness: Must pass all visible examples and handle edge cases
            2. Efficiency: Prefer iterative over recursive if both correct; prefer O(1) space if possible
            3. Simplicity: Most readable and straightforward
            4. Constraint compliance: Must follow all stated constraints
            
            Return ONLY the selected function code, nothing else.
            """,
            contexts_list=validated_candidates
        )

        # Step 5: Final safety revision - ensure exact function name and return type
        final_code = await self.revise(
            instruction=f"""Perform final safety check:
            1. Function name must match ENTRY POINT exactly
            2. Return type must match examples (int vs float matters)
            3. No extra imports or code outside function
            4. Must be a complete, runnable function
            
            If any issue, fix it. Return ONLY the final function code.
            """,
            context=final_code
        )

        return final_code