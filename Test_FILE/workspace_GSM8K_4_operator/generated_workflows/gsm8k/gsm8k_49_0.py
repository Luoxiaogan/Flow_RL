# Workflow ID: gsm8k_49_0
# Benchmark: gsm8k
# Data Indices: [213, 127]

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
            instruction="""Extract key components from the problem:
            - Numerical values and their context (e.g., units, relationships)
            - Entities involved (e.g., people, objects)
            - Goal of the problem (e.g., total quantity, number of items)
            Provide structured output.""",
            context=""
        )

        # Step 2: Solution Strategy
        strategies = await asyncio.gather(
            self.generate(
                instruction="Develop a sequential operations strategy based on the analysis.",
                context=analysis
            ),
            self.generate(
                instruction="Develop a rate-based strategy if applicable.",
                context=analysis
            ),
            self.generate(
                instruction="Develop a distribution strategy if applicable.",
                context=analysis
            ),
            self.generate(
                instruction="Develop a proportions strategy if applicable.",
                context=analysis
            )
        )
        strategy = await self.ensemble(
            instruction="Select the most appropriate strategy based on completeness and clarity.",
            contexts_list=strategies
        )

        # Step 3: Execution
        steps = strategy.split("\n")  # Assume strategy is a step-by-step plan
        results = []
        for step in steps:
            result = await self.generate(
                instruction=f"Perform the following calculation: {step}",
                context="\n".join(results)  # Pass previous results as context
            )
            validated = await self.revise(
                instruction="Verify the calculation and correct any errors.",
                context=result
            )
            results.append(validated)

        # Step 4: Final Answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the results.",
            context="\n".join(results)
        )

        return final_answer.strip()