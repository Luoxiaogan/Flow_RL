# Workflow ID: limr_143_0
# Benchmark: limr
# Data Indices: [216, 72]

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

        # Step 1: Initial Analysis and Classification
        initial_analysis = await self.generate(
            instruction="""Analyze the problem and classify it into one or more categories:
            - Is it algebraic, geometric, combinatorial, or probabilistic?
            - What are the key entities, constraints, and relationships?
            - What is the expected answer format?""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Explore algebraic solution strategies for: {initial_analysis}",
                context=""
            ),
            self.generate(
                instruction=f"Explore geometric solution strategies for: {initial_analysis}",
                context=""
            ),
            self.generate(
                instruction=f"Explore combinatorial solution strategies for: {initial_analysis}",
                context=""
            )
        )

        # Step 3: Intermediate Validation and Refinement
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine this solution strategy. Ensure logical consistency and accuracy.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesis and Decision-Making
        synthesis = await self.ensemble(
            instruction="Compare and synthesize these solution strategies. Select the most promising approach or combine insights from multiple strategies.",
            contexts_list=refined_strategies
        )

        # Step 5: Final Verification and Presentation
        final_solution = await self.revise(
            instruction="Perform final validation of the synthesized solution. Ensure it meets all problem constraints and requirements. Format the answer appropriately.",
            context=synthesis
        )

        return final_solution