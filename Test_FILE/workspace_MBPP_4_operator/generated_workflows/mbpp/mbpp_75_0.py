# Workflow ID: mbpp_75_0
# Benchmark: mbpp
# Data Indices: [180]

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

        # Step 1: Extract function name and infer requirements
        analysis = await self.generate(
            instruction="""Extract the function name from the assert statements and infer the problem type:
            - Identify the function name used in the assert statements.
            - Classify the problem as mathematical, list/array operation, string manipulation, or other.
            - List key requirements from the task description.""",
            context=""
        )

        # Step 2: Generate candidate solutions using parallel exploration
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a direct mathematical/logical solution:
                {analysis}
                - Use precise calculations and conditions.
                - Include necessary imports at the top.
                - Ensure proper indentation and syntax.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate an iterative solution:
                {analysis}
                - Process inputs step-by-step using loops.
                - Include necessary imports at the top.
                - Ensure proper indentation and syntax.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution leveraging Python's standard library:
                {analysis}
                - Use appropriate library functions (e.g., math, itertools).
                - Include necessary imports at the top.
                - Ensure proper indentation and syntax.""",
                context=analysis
            )
        )

        # Step 3: Validate and refine candidate solutions
        refined_candidates = []
        for candidate in candidates:
            refined = await self.revise(
                instruction="""Validate the solution against the test cases:
                - Check if the code passes all assert statements.
                - Fix any syntax errors or logical mistakes.
                - Improve clarity and readability.""",
                context=candidate
            )
            refined_candidates.append(refined)

        # Step 4: Synthesize the final solution
        final_solution = await self.ensemble(
            instruction="""Select the best-performing solution or combine insights from multiple candidates:
            - Prioritize solutions that pass all test cases.
            - Ensure the final solution includes necessary imports, proper indentation, and adheres to Python conventions.""",
            contexts_list=refined_candidates
        )

        return final_solution