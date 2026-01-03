# Workflow ID: limr_139_0
# Benchmark: limr
# Data Indices: [285, 221]

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

        # Step 1: Initial Analysis - Classify the problem and identify key components
        initial_analysis = await self.generate(
            instruction="""Analyze the problem:
            - Identify the mathematical domain (geometry, number theory, etc.)
            - Extract key variables, constraints, and relationships
            - Determine the expected answer format (integer between 000 and 999)
            - Highlight any special conditions or requirements""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop a solution using algebraic techniques",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop a solution using combinatorial reasoning",
                context=initial_analysis
            ),
            self.generate(
                instruction="Develop a solution using geometric interpretation",
                context=initial_analysis
            )
        )

        # Step 3: Validation - Critique and refine each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this strategy: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble Decision-Making - Synthesize the best solution
        best_solution = await self.ensemble(
            instruction="""Synthesize the best solution:
            - Evaluate each strategy for correctness, clarity, and efficiency
            - Select the most robust and elegant approach
            - Ensure the final answer is an integer between 000 and 999""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Verification - Double-check the solution
        verified_solution = await self.revise(
            instruction="Verify the final solution for accuracy and completeness",
            context=best_solution
        )

        return verified_solution