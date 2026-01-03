# Workflow ID: limr_132_0
# Benchmark: limr
# Data Indices: [283, 84]

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

        # Initial Analysis: Identify key components and potential solution strategies
        initial_analysis = await self.generate(
            instruction="""Analyze the problem structure and identify key components:
            - What are the main mathematical concepts involved?
            - What are the knowns and unknowns?
            - What are potential solution strategies?
            Provide a detailed breakdown.""",
            context=""
        )

        # Parallel Exploration: Explore multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Explore direct computation approach...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Explore proof techniques approach...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Explore optimization methods approach...",
                context=initial_analysis
            ),
            self.generate(
                instruction="Explore combinatorial analysis approach...",
                context=initial_analysis
            )
        )

        # Refinement and Validation: Refine each explored strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate this strategy: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Synthesis: Select the best solution or combine complementary insights
        synthesis = await self.ensemble(
            instruction="Evaluate and synthesize the refined strategies. Select the best solution or combine complementary insights.",
            contexts_list=refined_strategies
        )

        # Final Verification: Ensure the solution meets all requirements
        final_verification = await self.revise(
            instruction="Perform final verification of the synthesized solution. Ensure it meets all problem requirements and constraints.",
            context=synthesis
        )

        return final_verification