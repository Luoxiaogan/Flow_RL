# Workflow ID: gsm8k_129_0
# Benchmark: gsm8k
# Data Indices: [204, 235]

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

        # Initial Analysis
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, their units, and relationships:
            - Identify what is being asked.
            - Classify the problem type (rate, distribution, proportion, etc.).
            - List all known quantities and unknowns.""",
            context=""
        )

        # Solution Strategy Development
        strategy = await self.generate(
            instruction=f"""Based on the initial analysis:
            {initial_analysis}
            
            Develop a step-by-step solution strategy:
            - Define the sequence of operations needed.
            - Specify intermediate results to track.
            - Ensure all units are consistent.""",
            context=initial_analysis
        )

        # Parallel Solution Paths (if necessary)
        paths = await asyncio.gather(
            self.generate(
                instruction=f"""Solve using the primary strategy:
                {strategy}""",
                context=strategy
            ),
            self.generate(
                instruction=f"""Solve using an alternative approach, if applicable:
                {strategy}""",
                context=strategy
            )
        )

        # Ensemble to Choose Best Path
        best_path = await self.ensemble(
            instruction="Select the most accurate and efficient solution path.",
            contexts_list=paths
        )

        # Execution and Validation
        steps = best_path.split('\n')
        results = []
        for step in steps:
            if "Calculate" in step:
                result = await self.generate(
                    instruction=f"""Execute the following calculation:
                    {step}""",
                    context="\n".join(results)
                )
                validated_result = await self.revise(
                    instruction="Ensure the calculation is accurate and clear.",
                    context=result
                )
                results.append(validated_result)

        # Final Answer Extraction
        final_answer = await self.generate(
            instruction="Extract the final numerical answer from the results.",
            context="\n".join(results)
        )

        return final_answer