# Workflow ID: gsm8k_127_0
# Benchmark: gsm8k
# Data Indices: [276, 157]

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
        initial_analysis = await self.generate(
            instruction="""Extract key information from the problem:
            - Identify all numbers and their context
            - Determine the relationships between entities
            - List any constraints or conditions
            - Classify the problem type (e.g., rate, proportion, distribution)
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Parallel Exploration of Solution Strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Solve the problem using algebraic reasoning:
                Problem details: {initial_analysis}
                Show all steps and intermediate results.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using logical reasoning:
                Problem details: {initial_analysis}
                Focus on logical deductions and relationships.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Solve the problem using estimation:
                Problem details: {initial_analysis}
                Provide approximate results and validate against constraints.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Validate and refine this solution: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Synthesis
        final_solution = await self.ensemble(
            instruction="""Select the best solution or synthesize insights:
            - Ensure consistency with problem constraints
            - Prioritize exact calculations over approximations
            - Present the final numerical answer.""",
            contexts_list=refined_strategies
        )

        # Step 5: Final Output
        summarized_result = await self.summarize(
            instruction="Extract the final numerical answer from the solution.",
            context=final_solution
        )

        return summarized_result