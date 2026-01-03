# Workflow ID: gsm8k_11_0
# Benchmark: gsm8k
# Data Indices: [217, 83]

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
            instruction="""Analyze the problem structure:
            - Extract all numerical values and their units.
            - Identify relationships between entities.
            - Determine what the question is asking for.
            Provide a structured breakdown.""",
            context=""
        )

        # Step 2: Generate Solution Strategy
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {analysis}
            
            Generate a step-by-step solution strategy:
            - List all required calculations.
            - Specify the order of operations.
            - Highlight intermediate results to track.""",
            context=analysis
        )

        # Step 3: Parallel Validation
        direct_solution = await self.generate(
            instruction=f"""Compute the solution directly using the strategy:
            {strategy}""",
            context=strategy
        )
        alternative_validation = await self.generate(
            instruction=f"""Validate the solution using an alternative method:
            - Reverse calculations.
            - Cross-check units and relationships.
            Strategy: {strategy}""",
            context=strategy
        )

        # Step 4: Iterative Refinement
        validation_results = await asyncio.gather(direct_solution, alternative_validation)
        if any("error" in result.lower() for result in validation_results):
            refined_strategy = await self.revise(
                instruction="Refine the solution strategy to address errors.",
                context=strategy
            )
            final_solution = await self.generate(
                instruction=f"""Recompute the solution using the refined strategy:
                {refined_strategy}""",
                context=refined_strategy
            )
        else:
            final_solution = validation_results[0]

        # Step 5: Final Synthesis
        summary = await self.summarize(
            instruction="""Summarize the solution:
            - Include all intermediate results.
            - Present the final answer as a single numerical value.""",
            context=final_solution
        )

        return summary