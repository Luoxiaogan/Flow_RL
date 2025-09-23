# Workflow ID: gsm8k_71_0
# Benchmark: gsm8k
# Data Indices: [47, 299]

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

        # Step 1: Analyze the problem structure
        analysis = await self.generate(
            instruction="""Extract and classify all key elements from the problem:
            - Entities: What/who is involved?
            - Relationships: How do they interact?
            - Constraints: What conditions must be satisfied?
            - Goal: What is the desired outcome?
            Present the results in a structured format.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop a direct calculation approach based on the analysis.",
                context=analysis
            ),
            self.generate(
                instruction="Develop a proportional reasoning approach based on the analysis.",
                context=analysis
            ),
            self.generate(
                instruction="Develop a step-by-step breakdown approach based on the analysis.",
                context=analysis
            )
        )

        # Step 3: Refine and validate each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate the strategy: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesize the best solution
        final_solution = await self.ensemble(
            instruction="""Select the most accurate and complete solution:
            - Check for consistency with constraints.
            - Ensure all intermediate steps are valid.
            - Prefer simpler solutions if equally accurate.""",
            contexts_list=refined_strategies
        )

        # Step 5: Extract the final numerical answer
        answer = await self.generate(
            instruction="Extract the final numerical answer from the solution. Ensure it is precise and formatted correctly.",
            context=final_solution
        )

        return answer