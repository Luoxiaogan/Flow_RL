# Workflow ID: mbppplus_48_0
# Benchmark: mbppplus
# Data Indices: [226, 57, 277]

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

        # PHASE 1: Problem Decomposition & Intent Extraction
        decomposition = await self.generate(
            instruction="""Thoroughly analyze the programming problem. Extract:
            1. Core operation (e.g., sum, find max, validate, transform)
            2. Input data structures (list, tuple, set, nested structures)
            3. Output requirements (type, format, edge behavior)
            4. Key constraints (index bounds, type assumptions, duplicates)
            5. Likely edge cases (empty inputs, single elements, invalid indices)
            Structure your response as a bullet-point analysis with clear headers.""",
            context=""
        )

        # PHASE 2: Parallel Solution Generation (3 strategies)
        solution_attempts = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a Python function implementation using STRATEGY A: Direct & Efficient.
                - Use minimal, clean code (e.g., generator expressions, built-ins)
                - Assume valid inputs but add ONE critical edge case guard
                - Match exact return type from signature
                Problem context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation using STRATEGY B: Defensive & Explicit.
                - Use explicit loops and conditionals for clarity
                - Handle ALL edge cases: empty, single-element, type mismatches
                - Include input validation if implied by problem
                - Match exact return type from signature
                Problem context: {decomposition}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a Python function implementation using STRATEGY C: Algorithmic & Scalable.
                - Focus on time/space efficiency for large inputs
                - Use appropriate data structures (dicts, sets for lookups)
                - Document time complexity in comments
                - Match exact return type from signature
                Problem context: {decomposition}""",
                context=""
            )
        )

        # PHASE 3: Edge Case Synthesis & Stress Testing
        edge_cases = await self.generate(
            instruction=f"""Generate 5 brutal edge case scenarios for this problem.
            Include: empty inputs, extreme values, type mismatches, boundary indices, duplicates.
            Format as Python assert statements (even if hypothetical).
            Base this on the decomposition: {decomposition}""",
            context=""
        )

        # PHASE 4: Parallel Solution Revision (using edge cases)
        revised_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"""Revise this solution to handle edge cases. 
                Here are critical edge cases to address:
                {edge_cases}
                
                Requirements:
                - Preserve core logic but add guards/defaults
                - Never crash on invalid input (return sensible default or specified behavior)
                - Maintain exact return type
                - Keep code readable""",
                context=sol
            ) for sol in solution_attempts]
        )

        # PHASE 5: Ensemble Synthesis (Merge best parts)
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from these candidates:
            - Prioritize correctness on edge cases
            - Prefer clean, readable code
            - Ensure exact return type matching signature
            - Remove redundant comments or over-engineering
            - Preserve efficiency where possible
            Return ONLY the function implementation (no markdown, no explanations).""",
            contexts_list=revised_solutions
        )

        # PHASE 6: Meta-Validation (Self-check against problem)
        validated_solution = await self.revise(
            instruction=f"""Final validation pass. Given this problem description:
            {self.problem_text}
            
            And this solution:
            {final_solution}
            
            Check:
            1. Does function name and signature EXACTLY match?
            2. Are all edge cases from decomposition handled?
            3. Is return type correct?
            4. No external dependencies unless imported
            Fix any mismatches. Return ONLY the corrected function.""",
            context=final_solution
        )

        return validated_solution