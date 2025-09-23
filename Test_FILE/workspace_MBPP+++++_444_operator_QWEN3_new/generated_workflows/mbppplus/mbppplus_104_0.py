# Workflow ID: mbppplus_104_0
# Benchmark: mbppplus
# Data Indices: [83, 349, 311]

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

        # Step 1: Classify the problem type and extract key constraints
        classification = await self.generate(
            instruction="""Thoroughly analyze the programming problem and classify it by:
            1. Primary computational category (e.g., modular arithmetic, string manipulation, combinatorics, recurrence, lookup table)
            2. Input/output data types and structures
            3. Key algorithmic patterns required (iteration, recursion, dynamic programming, etc.)
            4. Critical edge cases (empty inputs, zeros, negatives, boundaries, duplicates)
            5. Mathematical properties or invariants that must be preserved
            Format your response as a structured analysis with clear section headers.""",
            context=""
        )

        # Step 2: Parallel solution generation and constraint extraction
        solution_draft, constraint_analysis = await asyncio.gather(
            self.generate(
                instruction=f"""Based on this classification:
                {classification}
                
                Generate a complete, correct Python function implementation that:
                - Matches the exact function signature from the problem
                - Handles all specified edge cases
                - Uses appropriate data structures and algorithms
                - Includes necessary imports inside the function if required
                - Returns the correct data type
                - Is efficient and readable
                Do not include any explanations — only the raw code block.""",
                context=classification
            ),
            self.generate(
                instruction=f"""From the problem classification:
                {classification}
                
                Extract 3-5 critical validation constraints or invariants that any correct solution MUST satisfy.
                Examples: "Must return integer for all inputs", "Must handle empty string without error", 
                "Result must be non-negative", "Must use modulo 12 arithmetic", etc.
                Format as a numbered list of precise, testable conditions.""",
                context=classification
            )
        )

        # Step 3: Solution verification and refinement loop
        current_solution = solution_draft
        for iteration in range(3):  # Max 3 refinement cycles
            verification = await self.generate(
                instruction=f"""Critically verify this solution against the problem requirements and constraints:
                Constraints to check:
                {constraint_analysis}
                
                Verification checklist:
                1. Does it handle all edge cases mentioned in classification?
                2. Are data types consistent (input/output)?
                3. Is the algorithm logically correct for the problem category?
                4. Are there any off-by-one errors or boundary issues?
                5. Does it match the expected function signature exactly?
                6. Would it pass the sample test cases shown?
                
                If any issues are found, describe them specifically. If perfect, respond "VALIDATED".""",
                context=current_solution
            )

            if "VALIDATED" in verification.upper():
                break
                
            # Revise based on verification feedback
            current_solution = await self.revise(
                instruction=f"""Fix all issues identified in verification:
                {verification}
                
                Requirements:
                - Preserve the original function signature
                - Maintain all edge case handling
                - Ensure type consistency
                - Improve clarity and correctness
                - Do not change the core algorithm unless logically flawed
                Return only the corrected code block.""",
                context=current_solution
            )
        else:
            # If we exhausted iterations, use ensemble to synthesize best version
            verification_final = await self.generate(
                instruction="Final verification attempt - identify any remaining subtle issues",
                context=current_solution
            )
            current_solution = await self.revise(
                instruction=f"Final polish based on: {verification_final}. Ensure maximum robustness.",
                context=current_solution
            )

        # Step 4: Generate alternative solutions in parallel for ensemble selection
        alternative_solutions = await asyncio.gather(
            self.generate(
                instruction=f"""Generate an ALTERNATIVE solution using a DIFFERENT algorithmic approach:
                Classification context: {classification}
                Original solution: {current_solution}
                Example: If original was iterative, try recursive or formula-based.
                Must be equally correct but structurally different.""",
                context=current_solution
            ),
            self.generate(
                instruction=f"""Generate a SIMPLIFIED solution focusing on minimalism and clarity:
                Classification context: {classification}
                Original solution: {current_solution}
                Remove any unnecessary complexity while preserving correctness.""",
                context=current_solution
            )
        )

        # Step 5: Ensemble select the optimal solution
        final_solution = await self.ensemble(
            instruction="""Select the BEST solution based on:
            1. Correctness (must handle all edge cases)
            2. Readability and clarity
            3. Efficiency (time/space complexity)
            4. Adherence to problem constraints
            5. Robustness against edge cases
            Return ONLY the selected code block - no explanations.""",
            contexts_list=[current_solution] + alternative_solutions
        )

        # Step 6: Final sanitization - ensure pure code output
        sanitized = await self.revise(
            instruction="""Extract ONLY the Python function code block.
            Remove any markdown, explanations, or non-code text.
            Ensure it starts with 'def' and includes all necessary imports inside.
            The output must be executable Python code and nothing else.""",
            context=final_solution
        )

        return sanitized