# Workflow ID: mbpp_30_0
# Benchmark: mbpp
# Data Indices: [98, 157]

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

        # Step 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract the function name from the test cases.
            - Identify input types and expected outputs.
            - Infer potential edge cases and constraints.
            - Summarize the task requirements.""",
            context=""
        )

        # Step 2: Parallel Exploration of Multiple Solutions
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on mathematical transformations:
                {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on string/list manipulations:
                {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution focusing on standard library usage:
                {analysis}""",
                context=analysis
            )
        )

        # Step 3: Validation and Iterative Refinement
        refined_candidates = []
        for candidate in candidates:
            for _ in range(3):  # Limit iterations to avoid infinite loops
                validation = await self.generate(
                    instruction=f"""Validate the solution against the test cases:
                    {candidate}""",
                    context=candidate
                )
                if "error" not in validation.lower():
                    refined_candidates.append(candidate)
                    break
                candidate = await self.revise(
                    instruction=f"""Revise the solution based on validation feedback:
                    {validation}""",
                    context=candidate
                )

        # Step 4: Ensemble Selection
        final_solution = await self.ensemble(
            instruction="""Select the best solution or synthesize a hybrid:
            - Prioritize solutions that pass all test cases.
            - Ensure the solution is syntactically correct and well-structured.""",
            contexts_list=refined_candidates
        )

        # Step 5: Final Output Preparation
        final_code = await self.revise(
            instruction="""Ensure the final code includes:
            - All necessary imports.
            - Proper indentation and formatting.
            - A clear function definition matching the test cases.""",
            context=final_solution
        )

        return final_code