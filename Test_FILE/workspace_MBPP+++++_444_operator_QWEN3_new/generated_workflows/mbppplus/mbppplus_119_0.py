# Workflow ID: mbppplus_119_0
# Benchmark: mbppplus
# Data Indices: [7, 223, 367]

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
        Dynamically adapts strategy based on problem decomposition.
        Uses parallel solution generation, validation, and ensemble selection.
        """
        import asyncio
        import re

        # STEP 1: Decompose the problem to understand its nature
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the problem. Extract:
            - Input types and structures (e.g., list of ints, single integer, tuple)
            - Expected output type and format
            - Core operation required (e.g., filtering, recursion, mathematical formula, string parsing)
            - Key edge cases (empty inputs, zero, negatives, duplicates, single elements)
            - Any constraints (time complexity, immutability, no extra imports, etc.)
            - Mathematical properties or known algorithms that might apply
            Format as a structured bullet list with clear headings.""",
            context=""
        )

        # STEP 2: Generate solution candidates in parallel from different paradigms
        strategy_instructions = [
            """Solve this problem using a mathematical or formulaic approach.
            Look for closed-form expressions, number theory, or algebraic simplifications.
            Avoid brute force. Focus on deriving a direct computation.
            Example: Bell numbers via recurrence, floor_Max via inequality analysis.
            Ensure code handles edge cases identified in the decomposition.""",
            
            """Solve this problem using an iterative or algorithmic approach.
            Use loops, conditionals, and standard library functions.
            Focus on clarity and direct translation of logic.
            Example: Filtering lists, string parsing, simple arithmetic loops.
            Ensure code handles edge cases identified in the decomposition.""",
            
            """Solve this problem using recursion or dynamic programming.
            Break into subproblems, use memoization if needed.
            Example: Bell numbers via DP table, combinatorial problems.
            Ensure base cases are correct and handle edge cases from decomposition."""
        ]

        candidate_tasks = [
            self.generate(instruction=instr, context=decomposition)
            for instr in strategy_instructions
        ]
        raw_candidates = await asyncio.gather(*candidate_tasks)

        # STEP 3: Validate each candidate for correctness and edge case handling
        validation_tasks = [
            self.revise(
                instruction="""Critically evaluate this code for correctness. Check:
                - Does it handle ALL edge cases mentioned in the decomposition (empty, zero, negatives, etc.)?
                - Does it match the exact function signature (name, parameters)?
                - Does it return the correct data type (list vs tuple vs int)?
                - Are there logical errors (e.g., off-by-one, mutation during iteration, integer division)?
                - Is it unnecessarily inefficient for large inputs?
                If valid, return 'VALID'. Otherwise, return a concise bulleted list of flaws.""",
                context=candidate
            )
            for candidate in raw_candidates
        ]
        validations = await asyncio.gather(*validation_tasks)

        # Filter to only valid candidates
        valid_candidates = [
            raw_candidates[i] 
            for i, v in enumerate(validations) 
            if v.strip().upper() == 'VALID'
        ]

        # If no valid candidates, trigger fallback: re-decompose with error context
        if len(valid_candidates) == 0:
            error_summary = "\n".join([f"Candidate {i+1} failed: {v}" for i, v in enumerate(validations)])
            decomposition = await self.generate(
                instruction=f"""Re-analyze the problem considering these validation failures:
                {error_summary}
                
                Re-extract:
                - What was misunderstood in the initial decomposition?
                - What edge cases were missed?
                - What paradigm is most likely correct?
                Output revised structured analysis.""",
                context=decomposition
            )
            
            # Regenerate candidates with new decomposition
            candidate_tasks = [
                self.generate(instruction=instr, context=decomposition)
                for instr in strategy_instructions
            ]
            raw_candidates = await asyncio.gather(*candidate_tasks)
            
            # Re-validate
            validation_tasks = [
                self.revise(
                    instruction="""Critically evaluate this code for correctness. Check:
                    - Edge case handling
                    - Signature match
                    - Return type correctness
                    - Logical errors
                    - Efficiency
                    Return 'VALID' if perfect, else list flaws concisely.""",
                    context=candidate
                )
                for candidate in raw_candidates
            ]
            validations = await asyncio.gather(*validation_tasks)
            valid_candidates = [
                raw_candidates[i] 
                for i, v in enumerate(validations) 
                if v.strip().upper() == 'VALID'
            ]
            
            # If still no valid, take the least flawed candidate
            if len(valid_candidates) == 0:
                # Find candidate with shortest (least severe) validation feedback
                min_idx = min(range(len(validations)), key=lambda i: len(validations[i]))
                valid_candidates = [raw_candidates[min_idx]]

        # STEP 4: Ensemble - select the best valid candidate
        selected_solution = await self.ensemble(
            instruction="""You are given 1-3 valid candidate solutions.
            Select the SINGLE BEST one based on:
            - Correctness (must handle all edge cases)
            - Adherence to function signature and return type
            - Efficiency (avoid unnecessary complexity)
            - Clarity and simplicity
            - Alignment with reference solution style (minimal, direct)
            Output ONLY the code of the selected solution. No explanations, no markdown.
            If multiple are equally good, pick the most elegant one.""",
            contexts_list=valid_candidates
        )

        # STEP 5: Final polish - ensure production-ready code
        final_code = await self.revise(
            instruction="""Polish this code for final submission. Ensure:
            - Function name and parameters EXACTLY match required signature
            - All necessary imports are INSIDE the function if used (e.g., 'import math')
            - NO extra print/debug statements
            - Return type is correct (e.g., list vs tuple)
            - Code is minimal, clean, and follows Python best practices
            - No type hints or extra comments unless in original signature
            Output ONLY the final function code. Nothing else.""",
            context=selected_solution
        )

        return final_code