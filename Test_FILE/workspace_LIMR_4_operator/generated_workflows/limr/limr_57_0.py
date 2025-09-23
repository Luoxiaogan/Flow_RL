# Workflow ID: limr_57_0
# Benchmark: limr
# Data Indices: [135, 156]

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

        # Step 1: Initial Problem Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem structure:
            1. Identify the main mathematical domain (geometry, number theory, etc.).
            2. Extract key components (equations, variables, constraints).
            3. Propose potential solution strategies.
            Provide structured output.""",
            context=""
        )

        # Step 2: Parallel Strategy Exploration
        strategies = await asyncio.gather(
            self.generate(
                instruction="Explore algebraic/analytical methods...", context=analysis
            ),
            self.generate(
                instruction="Explore geometric/visual methods...", context=analysis
            ),
            self.generate(
                instruction="Explore combinatorial/logical methods...", context=analysis
            )
        )

        # Step 3: Iterative Refinement
        refined_strategies = []
        for strategy in strategies:
            refined = await self.revise(
                instruction="Refine the strategy by adding specific steps, validating assumptions, and ensuring precision.",
                context=strategy
            )
            refined_strategies.append(refined)

        # Step 4: Ensemble Selection
        final_solution = await self.ensemble(
            instruction="""Select the best solution:
            - Evaluate correctness and completeness.
            - Ensure the answer is an integer between 000 and 999.
            - Prefer simpler, more elegant solutions if multiple are valid.""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Validation
        validation = await self.revise(
            instruction="Validate the final solution by checking all steps, assumptions, and constraints.",
            context=final_solution
        )

        return validation