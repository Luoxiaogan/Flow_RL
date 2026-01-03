# Workflow ID: mbppplus_120_0
# Benchmark: mbppplus
# Data Indices: [193, 66, 244]

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
        import math

        # Generate three diverse candidate solutions in parallel
        candidate_instructions = [
            """You are an expert Python programmer known for mathematical precision.
            Implement the required function with rigorous attention to:
            - Correct algorithmic logic (e.g., proper regex patterns, mathematical formulas)
            - Precise type handling (return exactly what's specified: string, int, list, etc.)
            - Numerical edge cases (zero, negative numbers, floating point issues)
            - Include necessary imports inside the function if needed.
            Return ONLY the function implementation with no additional text.""",
            
            """You are an expert Python programmer known for robust edge-case handling.
            Implement the required function with obsessive attention to:
            - All possible edge cases (empty inputs, single elements, duplicates, invalid types)
            - Defensive programming (input validation, type guards, boundary checks)
            - Explicit handling of corner cases mentioned in problem domain overview
            - Include necessary imports inside the function if needed.
            Return ONLY the function implementation with no additional text.""",
            
            """You are an expert Python programmer known for clean, simple, readable code.
            Implement the required function with focus on:
            - Minimal, elegant logic that's easy to understand
            - Avoiding unnecessary complexity or over-engineering
            - Clear variable names and straightforward control flow
            - Include necessary imports inside the function if needed.
            Return ONLY the function implementation with no additional text."""
        ]

        candidates = await asyncio.gather(
            *[self.generate(instruction=instr, context="") for instr in candidate_instructions]
        )

        # Validate each candidate independently
        validation_instruction = """Critically analyze this code for hidden flaws. Check for:
        1. Type mismatches (e.g., returning list when tuple expected)
        2. Unhandled edge cases (empty input, zero, negatives, single elements, duplicates)
        3. Off-by-one errors or boundary condition failures
        4. Regex or pattern logic flaws (e.g., greedy vs lazy matching, anchors)
        5. Mathematical errors (incorrect formulas, precision issues, domain restrictions)
        6. Performance bottlenecks that could fail under large inputs
        7. Deviation from required function signature or return type
        Return a bulleted list of specific, actionable flaws. If no flaws found, return 'VALID'."""

        validations = await asyncio.gather(
            *[self.generate(instruction=validation_instruction, context=cand) for cand in candidates]
        )

        # Revise each candidate based on its validation report
        revised_candidates = await asyncio.gather(
            *[self.revise(
                instruction=f"""Incorporate ALL fixes from the validation report below.
                Do NOT change parts that are working correctly.
                Preserve exact function signature and return type.
                Add comments ONLY for non-obvious logic or edge-case handling.
                Ensure all identified edge cases are explicitly handled.
                Return ONLY the revised function implementation with no additional text.
                
                Validation Report:
                {validation}""",
                context=candidate
            ) for candidate, validation in zip(candidates, validations)]
        )

        # Ensemble: Synthesize best elements into final solution
        final_solution = await self.ensemble(
            instruction="""You are given three candidate solutions to the same programming problem.
            Each has been validated and revised. Synthesize the best elements into one optimal solution.
            Prioritize in this order:
            1. CORRECTNESS: Must handle all edge cases and pass all test cases.
            2. SIGNATURE COMPLIANCE: Exact function name, parameters, and return type.
            3. CLARITY: Clean, readable code with comments only where logic is non-obvious.
            4. EFFICIENCY: Avoid unnecessary complexity or performance bottlenecks.
            
            If candidates disagree on logic, prefer the solution with explicit edge-case handling.
            If all are equivalent, choose the simplest implementation.
            Return ONLY the final function code with imports inside the function if needed.
            NO additional text, explanations, or markdown.""",
            contexts_list=revised_candidates
        )

        return final_solution