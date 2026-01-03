# Workflow ID: gsm8k_126_0
# Benchmark: gsm8k
# Data Indices: [121, 273]

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

        # Initial analysis to extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships.
            Classify the problem type (sequential operations, rate problems, distribution, proportions, multi-entity).
            Identify what the question is asking for.""",
            context=""
        )

        # Generate multiple solution paths based on the classification
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"Generate solution path focusing on sequential operations: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Generate solution path focusing on rate problems: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Generate solution path focusing on distribution: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Generate solution path focusing on proportions: {initial_analysis}",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"Generate solution path focusing on multi-entity scenarios: {initial_analysis}",
                context=initial_analysis
            )
        )

        # Validate and refine each solution path
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine this solution path. Ensure all steps are accurate and logically follow from previous steps.",
                context=path
            ) for path in solution_paths]
        )

        # Synthesize the best solution or combine insights from different paths
        final_solution = await self.ensemble(
            instruction="Synthesize the best solution from the refined paths. Combine insights if multiple paths are valid.",
            contexts_list=refined_paths
        )

        # Condense the final solution into a concise summary
        summary = await self.summarize(
            instruction="Summarize the final solution, showing only the essential steps and the final numerical answer.",
            context=final_solution
        )

        return summary