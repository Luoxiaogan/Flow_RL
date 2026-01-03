# Workflow ID: humaneval_28_0
# Benchmark: humaneval
# Data Indices: [70, 13]

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

        # Phase 1: Problem Analysis and Classification
        problem_analysis = await self.generate(
            instruction="""Perform a deep analysis of this code generation problem:

1. Extract the exact function signature and ENTRY POINT name.
2. Analyze the docstring examples to infer the core algorithmic pattern.
3. Classify the problem type (e.g., mathematical, list manipulation, string processing).
4. Identify edge cases from examples (empty inputs, duplicates, single elements).
5. Determine expected input/output types and any constraints.
6. Hypothesize at least two different approaches to solve this problem.

Format your response as a structured analysis with clear sections.""",
            context=""
        )

        # Phase 2: Parallel Strategy Generation
        strategy_instructions = [
            """Generate a Python function that solves the problem by directly implementing the pattern shown in the examples. Focus on literal interpretation of the examples, step by step. Include comments explaining each step. Handle edge cases explicitly.""",
            """Generate a Python function that solves the problem by generalizing the underlying mathematical or logical principle. Use minimal code and avoid unnecessary steps. Focus on elegance and efficiency. Include a brief explanation of the generalization.""",
            """Generate a Python function that solves the problem using Python built-in functions or standard library modules (if applicable). Prioritize readability and Pythonic style. Include comments on why this approach is suitable."""
        ]

        candidate_solutions = await asyncio.gather(
            *[self.generate(instruction=instr, context=problem_analysis) for instr in strategy_instructions]
        )

        # Phase 3: Parallel Refinement
        refined_candidates = []
        for candidate in candidate_solutions:
            refined = await self.revise(
                instruction=f"""Revise this code to ensure it meets all specifications:

1. Function name must exactly match the ENTRY POINT.
2. Return type must match examples precisely (int vs float, list structure, etc.).
3. Handle all edge cases mentioned or implied in the problem.
4. Avoid over-engineering — implement exactly what's specified.
5. Ensure code is clean, readable, and follows Python best practices.
6. Add comments only if they clarify non-obvious logic.

Problem Analysis for context:
{problem_analysis}""",
                context=candidate
            )
            refined_candidates.append(refined)

        # Phase 4: Ensemble Selection
        final_solution = await self.ensemble(
            instruction=f"""Select the best solution from the candidates below based on:

1. Correctness: Does it match all examples in the docstring?
2. Simplicity: Is it the most straightforward implementation?
3. Robustness: Does it handle edge cases correctly?
4. Precision: Does it return the exact types and structures specified?

If no candidate is clearly superior, synthesize a new solution combining the best elements of each.

Problem Analysis for reference:
{problem_analysis}

Return ONLY the final Python function code, with no additional text or explanations.""",
            contexts_list=refined_candidates
        )

        # Phase 5: Final Validation and Cleanup
        validated_solution = await self.revise(
            instruction="""Final check: Ensure the code is ready for submission.

1. Verify function name matches ENTRY POINT exactly.
2. Remove any unnecessary comments or debug statements.
3. Ensure no imports are included (they will be auto-added).
4. Return ONLY the function definition, nothing else.

If any issues are found, fix them immediately.""",
            context=final_solution
        )

        return validated_solution