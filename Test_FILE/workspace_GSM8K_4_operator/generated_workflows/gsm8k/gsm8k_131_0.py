# Workflow ID: gsm8k_131_0
# Benchmark: gsm8k
# Data Indices: [267, 154]

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

        # Initial Analysis: Extract information and classify problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract all numerical values, entities, and relationships.
            - Classify the problem type (e.g., sequential operations, rate problems, distribution, proportions, multi-entity).
            - Identify what the question asks for.
            Provide structured output.""",
            context=""
        )

        # Parallel Approaches: Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Generate a solution path using mathematical approach: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Generate a solution path using logical reasoning: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Generate a solution path using practical estimation: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Refinement: Improve each solution path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine the solution path: {path}. Correct errors and add missing details.",
                context=path
            ) for path in solution_paths]
        )

        # Ensemble Decision: Select the best solution
        best_solution = await self.ensemble(
            instruction="Select the most accurate and complete solution from the refined paths.",
            contexts_list=refined_paths
        )

        # Final Validation: Validate and finalize the solution
        final_solution = await self.generate(
            instruction=f"Validate the solution: {best_solution}. Ensure it meets the problem requirements and present the final answer.",
            context=best_solution
        )

        return final_solution