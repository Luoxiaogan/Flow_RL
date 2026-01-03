# Workflow ID: gsm8k_46_0
# Benchmark: gsm8k
# Data Indices: [240, 197]

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

        # Initial Analysis: Extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem.
            Classify the problem type (e.g., rate, distribution, proportion).
            Identify what the question asks for and any constraints.""",
            context=""
        )

        # Parallel Exploration: Generate multiple solution paths
        solution_paths = await asyncio.gather(
            self.generate(
                instruction="Solve using direct calculation. Show all steps and intermediate results.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using estimation. Provide approximate values and reasoning.",
                context=initial_analysis
            ),
            self.generate(
                instruction="Solve using logical reasoning. Focus on relationships and constraints.",
                context=initial_analysis
            )
        )

        # Validation and Refinement: Critique and improve each path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution path: {path}",
                context=path
            ) for path in solution_paths]
        )

        # Summarize Intermediate Results: Highlight key findings
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction="Condense this solution path into key findings and intermediate results.",
                context=path
            ) for path in refined_paths]
        )

        # Ensemble Synthesis: Combine the best elements of the paths
        final_solution = await self.ensemble(
            instruction="""Synthesize the best solution from the provided paths.
            Criteria:
            - Numerical precision
            - Logical consistency
            - Completeness of reasoning""",
            contexts_list=summaries
        )

        # Final Validation: Ensure the answer is numerically exact
        final_answer = await self.revise(
            instruction="Verify the final solution and extract the numerical answer.",
            context=final_solution
        )

        return final_answer