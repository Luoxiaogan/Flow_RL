# Workflow ID: mbppplus_132_0
# Benchmark: mbppplus
# Data Indices: [132, 106]

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
        import json

        # Step 1: Decompose the problem into facets to guide strategy
        facets = await self.decompose(
            instruction="""Analyze this programming problem and break it into key facets:
            1. Input types and constraints (e.g., sorted array, positive integers, strings)
            2. Output requirements (type, format, edge behavior)
            3. Algorithmic hints (e.g., "first occurrence" suggests binary search, "set bits" suggests bit manipulation)
            4. Known edge cases (empty input, single element, duplicates, boundaries)
            5. Performance expectations (if any)
            Return each facet as a separate subproblem with clear description.""",
            context=""
        )

        # Convert facets to readable context
        facets_context = "\n".join([f"{f['id']}: {f['description']}" for f in facets])

        # Step 2: Generate multiple solution strategies in parallel
        strategy_instructions = [
            f"""Based on problem facets:
            {facets_context}
            
            Strategy 1: Optimal Algorithm Approach
            - Assume the problem expects an optimal (e.g., O(log n) or O(1)) solution
            - Use advanced techniques like binary search, bit manipulation, or mathematical formulas
            - Handle all edge cases explicitly
            - Return code matching exact function signature""",
            
            f"""Based on problem facets:
            {facets_context}
            
            Strategy 2: Readable & Defensive Approach
            - Prioritize clarity and explicit edge case handling over performance
            - Use linear scans or simple loops if appropriate
            - Include guard clauses for empty/negative edge cases
            - Return code matching exact function signature""",
            
            f"""Based on problem facets:
            {facets_context}
            
            Strategy 3: Mathematical/Formulaic Approach
            - Look for mathematical patterns, formulas, or cycle detection
            - Especially relevant for bit manipulation, counting, or sequence problems
            - Derive closed-form solutions if possible
            - Return code matching exact function signature""",
            
            f"""Based on problem facets:
            {facets_context}
            
            Strategy 4: Lateral Thinking Wildcard
            - Ignore obvious approaches
            - Is there a bit-level, combinatorial, or obscure insight that simplifies this?
            - Consider lookup tables, precomputation, or language-specific tricks
            - Return code matching exact function signature"""
        ]

        # Generate candidate solutions in parallel
        candidate_tasks = [
            self.generate(instruction=instr, context="")
            for instr in strategy_instructions
        ]
        candidates = await asyncio.gather(*candidate_tasks)

        # Step 3: Validate each candidate with self-generated edge cases
        async def validate_and_revise(candidate, attempt=0):
            try:
                # Generate and run edge case tests
                test_result = await self.programmer(
                    instruction=f"""Given this candidate solution:
                    {candidate}
                    
                    Generate and execute 5 edge test cases including:
                    - Empty input
                    - Single element
                    - All duplicates
                    - Target absent
                    - Boundary values
                    Return any failures with specific error messages. If all pass, return 'ALL_TESTS_PASSED'.""",
                    context=candidate,
                    max_retries=1
                )
                
                if "ALL_TESTS_PASSED" in test_result:
                    return candidate
                elif attempt < 2:  # Allow up to 2 revisions
                    revised = await self.revise(
                        instruction=f"""The following solution failed edge case tests:
                        {test_result}
                        
                        Revise the code to fix these failures without breaking existing functionality.
                        Preserve exact function signature and return type.
                        Add explicit edge case handling where missing.""",
                        context=candidate
                    )
                    return await validate_and_revise(revised, attempt + 1)
                else:
                    return None  # Mark as failed after max revisions
            except Exception:
                return None

        # Validate all candidates with revision capability
        validated_candidates = await asyncio.gather(
            *[validate_and_revise(candidate) for candidate in candidates]
        )

        # Filter out failed candidates
        successful_candidates = [c for c in validated_candidates if c is not None]
        
        if not successful_candidates:
            # Fallback: return simplest working solution with warning
            fallback = await self.generate(
                instruction="""All advanced strategies failed. 
                Implement a simple, brute-force solution that is guaranteed to work correctly.
                Prioritize correctness over performance. Handle all edge cases explicitly.
                Include detailed comments explaining edge case handling.
                Return code matching exact function signature.""",
                context=facets_context
            )
            return fallback

        # Step 4: Ensemble - select or synthesize best solution
        final_solution = await self.ensemble(
            instruction="""You are an expert code reviewer selecting the best solution.
            Criteria:
            1. Correctness (must pass all edge cases)
            2. Efficiency (prefer optimal algorithms when appropriate)
            3. Readability (clear variable names, logical flow)
            4. Robustness (explicit edge case handling)
            
            If multiple solutions are equally good, synthesize a hybrid that combines:
            - The algorithmic efficiency of the optimal approach
            - The explicit edge case handling of the defensive approach
            - Any mathematical insights from the formulaic approach
            
            Ensure the final code:
            - Matches the exact function signature from the problem
            - Returns correct data types
            - Has no external dependencies beyond standard library
            - Is production-ready and self-contained""",
            contexts_list=successful_candidates
        )

        # Step 5: Final verification summary (acts as correctness proof)
        verification = await self.summarize(
            instruction="""Produce a 3-sentence correctness argument for this solution:
            1. What invariant does the algorithm maintain?
            2. How are edge cases handled?
            3. Why does it terminate with the correct result?
            
            If you cannot write a coherent correctness argument, flag this by starting with 'UNVERIFIED:'""",
            context=final_solution
        )

        # If verification fails, return with warning
        if verification.startswith("UNVERIFIED:"):
            final_solution = f"# WARNING: Solution may have correctness issues\n# {verification}\n{final_solution}"

        return final_solution