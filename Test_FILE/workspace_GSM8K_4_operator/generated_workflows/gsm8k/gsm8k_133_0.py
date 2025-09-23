# Workflow ID: gsm8k_133_0
# Benchmark: gsm8k
# Data Indices: [231, 222]

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

        # Step 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Analyze the problem:
            - Extract all numbers, units, and relationships.
            - Identify what is being asked.
            - Classify the problem type (e.g., rate, proportion, distribution).
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Develop a sequential solution strategy:
                {analysis}
                Focus on step-by-step calculations.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a proportional reasoning strategy:
                {analysis}
                Focus on scaling and ratios.""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Develop a distribution-based strategy:
                {analysis}
                Focus on dividing quantities and handling remainders.""",
                context=analysis
            )
        )

        # Step 3: Execute and Validate Strategies
        async def execute_and_validate(strategy):
            steps = await self.generate(
                instruction=f"""Execute the strategy step-by-step:
                {strategy}
                Show all calculations and intermediate results.""",
                context=strategy
            )
            validated_steps = await self.revise(
                instruction=f"""Validate the calculations:
                {steps}
                Check for errors and ensure numerical accuracy.""",
                context=steps
            )
            return validated_steps

        validated_strategies = await asyncio.gather(
            *[execute_and_validate(s) for s in strategies]
        )

        # Step 4: Synthesize Best Solution
        best_solution = await self.ensemble(
            instruction="""Compare and select the best solution:
            - Ensure logical consistency.
            - Prioritize numerical accuracy.
            - Choose the most straightforward approach.""",
            contexts_list=validated_strategies
        )

        # Step 5: Final Output
        final_answer = await self.summarize(
            instruction="""Extract the final numerical answer:
            - Include only the single numerical value.
            - Ensure it matches the problem's requirements.""",
            context=best_solution
        )

        return final_answer.strip()