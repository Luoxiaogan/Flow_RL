# Workflow ID: humaneval_18_0
# Benchmark: humaneval
# Data Indices: [130, 8]

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

        # Step 1: Extract structured problem understanding
        problem_analysis = await self.generate(
            instruction="""Thoroughly analyze the function specification and extract:
            1. Function purpose in one clear sentence
            2. All example input-output pairs (verbatim)
            3. Explicit formulas, recurrence relations, or algorithms mentioned
            4. Edge cases (explicit or implied)
            5. Return type requirements (int, float, list, etc.)
            6. Any constraints on input values
            Format as numbered bullet points with clear headings.""",
            context=""
        )

        # Step 2: Generate three parallel solution strategies
        iterative_approach, recursive_approach, formulaic_approach = await asyncio.gather(
            self.generate(
                instruction=f"""Generate an ITERATIVE solution:
                - Start with base cases from examples
                - Use loops to build up solution
                - Pay attention to index boundaries
                - Match return types exactly (int vs float)
                - Handle edge cases explicitly
                Problem context: {problem_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a RECURSIVE solution (if applicable):
                - Define clear base cases
                - Ensure termination conditions
                - Consider memoization if performance might matter
                - Match return types exactly
                - Handle edge cases
                Problem context: {problem_analysis}""",
                context=""
            ),
            self.generate(
                instruction=f"""Generate a FORMULA-BASED solution:
                - Look for mathematical patterns in examples
                - Derive closed-form expressions if possible
                - Handle special cases separately
                - Ensure type precision
                Problem context: {problem_analysis}""",
                context=""
            )
        )

        # Step 3: Adversarial critique of each approach
        iterative_critique, recursive_critique, formulaic_critique = await asyncio.gather(
            self.revise(
                instruction="""Critique this solution as a harsh code reviewer:
                1. Does it match ALL example outputs exactly?
                2. Are return types correct (int vs float)?
                3. Any index errors or boundary issues?
                4. Unhandled edge cases?
                5. Does function name match ENTRY POINT?
                6. Any deviations from specification?
                Be brutally honest and specific.""",
                context=iterative_approach
            ),
            self.revise(
                instruction="""Critique this solution as a harsh code reviewer:
                1. Does it match ALL example outputs exactly?
                2. Are return types correct (int vs float)?
                3. Any infinite recursion risks?
                4. Unhandled edge cases?
                5. Does function name match ENTRY POINT?
                6. Any deviations from specification?
                Be brutally honest and specific.""",
                context=recursive_approach
            ),
            self.revise(
                instruction="""Critique this solution as a harsh code reviewer:
                1. Does it match ALL example outputs exactly?
                2. Are return types correct (int vs float)?
                3. Any mathematical errors?
                4. Unhandled edge cases?
                5. Does function name match ENTRY POINT?
                6. Any deviations from specification?
                Be brutally honest and specific.""",
                context=formulaic_approach
            )
        )

        # Step 4: Ensemble synthesis - combine best elements
        final_solution = await self.ensemble(
            instruction="""You are a senior engineer synthesizing the best solution:
            - Prioritize correctness on all documented examples
            - Ensure perfect handling of edge cases
            - Match return types exactly (int vs float matters)
            - Use clearest, most Pythonic implementation
            - Function name MUST match ENTRY POINT exactly
            - If no candidate is perfect, combine strongest elements
            - Resolve all critique issues explicitly
            Output ONLY the final Python function code.""",
            contexts_list=[
                f"ITERATIVE APPROACH:\n{iterative_approach}\n\nCRITIQUE:\n{iterative_critique}",
                f"RECURSIVE APPROACH:\n{recursive_approach}\n\nCRITIQUE:\n{recursive_critique}",
                f"FORMULAIC APPROACH:\n{formulaic_approach}\n\nCRITIQUE:\n{formulaic_critique}"
            ]
        )

        # Step 5: Final verification pass (author mode)
        verified_solution = await self.revise(
            instruction=f"""You are the original problem author verifying the solution:
            1. Check EACH example in the specification against this code
            2. Verify return types match exactly (int vs float)
            3. Confirm function name matches ENTRY POINT
            4. Ensure no extra features beyond specification
            5. Fix any discrepancies without adding complexity
            Problem context: {problem_analysis}
            Output ONLY the corrected Python function code.""",
            context=final_solution
        )

        return verified_solution