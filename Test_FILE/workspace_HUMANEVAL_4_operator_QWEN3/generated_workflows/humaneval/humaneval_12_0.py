# Workflow ID: humaneval_12_0
# Benchmark: humaneval
# Data Indices: [154, 137]

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

        # Phase 1: Deep problem decomposition and strategy classification
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the problem specification. Extract:
            1. Input types and structures (string, int, float, mixed, etc.)
            2. Output type and format requirements (must match examples exactly)
            3. Core transformation or logic pattern (substring, rotation, comparison, math, etc.)
            4. Edge cases implied by examples (empty inputs, type mismatches, boundary conditions)
            5. Any special parsing rules (e.g., comma as decimal separator)
            6. Function name that must be used (ENTRY POINT)
            Present as a structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Parallel generation of diverse solution candidates
        candidate_a, candidate_b, candidate_c = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution by directly mimicking the examples.
                Focus on literal pattern matching and example replication.
                Use the exact function name from ENTRY POINT.
                Prioritize correctness on provided examples over generalization.
                Handle edge cases shown in examples.
                Return only raw Python code, no explanations.
                Problem context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution by deriving the underlying algorithm.
                Generalize from examples to find the core logic or formula.
                Use the exact function name from ENTRY POINT.
                Ensure return types match examples precisely.
                Optimize for clarity and correctness.
                Return only raw Python code, no explanations.
                Problem context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a solution with strict type handling and conversion.
                Pay special attention to type mismatches (str/int/float) and parsing rules.
                Use the exact function name from ENTRY POINT.
                Ensure outputs match example types exactly (int vs float matters).
                Handle all edge cases involving type conversion.
                Return only raw Python code, no explanations.
                Problem context: {decomposition}""",
                context=""
            )
        )

        candidates = [candidate_a, candidate_b, candidate_c]
        validated_candidates = []

        # Phase 3: Conditional validation and iterative refinement
        for candidate in candidates:
            current_code = candidate
            for attempt in range(3):  # Max 2 revisions + original
                validation = await self.generate(
                    instruction=f"""Simulate executing this code against ALL examples in the docstring.
                    Check: 
                    - Does it return correct values?
                    - Are return types exact matches (int vs float, str vs num)?
                    - Are edge cases handled?
                    - Is the function name correct?
                    If perfect, respond ONLY with "VALID".
                    If flawed, describe exactly what's wrong and how to fix it.
                    Code to validate:
                    {current_code}""",
                    context=current_code
                )
                
                if "VALID" in validation.upper():
                    validated_candidates.append(current_code)
                    break
                else:
                    if attempt < 2:  # Only revise twice
                        current_code = await self.revise(
                            instruction=f"""Fix the code based on this validation feedback:
                            {validation}
                            Preserve the core logic but correct the errors.
                            Maintain exact function name and return types.
                            Return only raw Python code, no explanations.""",
                            context=current_code
                        )
                    else:
                        # Give up on this candidate after 2 revisions
                        pass

        # If no candidates survived, use original candidates as fallback
        if not validated_candidates:
            validated_candidates = candidates

        # Phase 4: Ensemble synthesis of best solution
        final_solution = await self.ensemble(
            instruction="""Synthesize the best possible solution from the candidates.
            Combine strengths: 
            - Use the most robust logic
            - Preserve correct type handling
            - Ensure all edge cases are covered
            - Match return types exactly as in examples
            - Use the exact ENTRY POINT function name
            - Keep code minimal and precise — no over-engineering
            Return ONLY raw Python code, nothing else.""",
            contexts_list=validated_candidates
        )

        # Phase 5: Final sanity check
        sanity_check = await self.generate(
            instruction=f"""Final verification: 
            Does this code:
            1. Use the correct function name?
            2. Match all example outputs and types exactly?
            3. Handle all edge cases from examples?
            If yes, return the code unchanged.
            If no, return corrected code.
            Return ONLY raw Python code.
            Code:
            {final_solution}""",
            context=final_solution
        )

        # Clean output: remove markdown, explanations, ensure pure code
        code_lines = []
        for line in sanity_check.split('\n'):
            if line.strip() and not line.strip().startswith(('