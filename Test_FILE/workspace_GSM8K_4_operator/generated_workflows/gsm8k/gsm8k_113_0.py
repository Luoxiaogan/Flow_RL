# Workflow ID: gsm8k_113_0
# Benchmark: gsm8k
# Data Indices: [168, 32]

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
            instruction="""Extract key components from the problem:
            - Identify all numerical values and their units.
            - Determine relationships between entities (e.g., proportions, rates).
            - List constraints or conditions.
            - Clarify the goal or final question.
            Format the output as a structured list.""",
            context=""
        )

        # Step 2: Strategy Identification
        strategy = await self.generate(
            instruction=f"""Based on the analysis:
            {initial_analysis}
            
            Classify the problem type and identify the best solution strategy:
            - Is it a rate, proportion, distribution, or other type?
            - What sequence of operations is needed?
            - Are approximations acceptable or must calculations be exact?""",
            context=initial_analysis
        )

        # Step 3: Parallel Solution Exploration
        direct_solution = self.generate(
            instruction=f"""Solve the problem using the identified strategy:
            {strategy}
            Show all intermediate steps and calculations.""",
            context=initial_analysis
        )
        alternative_solution = self.generate(
            instruction=f"""Solve the problem using an alternative approach (e.g., estimation or unit analysis):
            {strategy}""",
            context=initial_analysis
        )
        validation_check = self.generate(
            instruction=f"""Validate the problem's constraints and ensure consistency:
            {strategy}""",
            context=initial_analysis
        )
        results = await asyncio.gather(direct_solution, alternative_solution, validation_check)

        # Step 4: Ensemble Synthesis
        final_solution = await self.ensemble(
            instruction="""Synthesize the results from multiple paths:
            - Resolve discrepancies between solutions.
            - Select the most accurate and reliable result.
            - Ensure the final answer matches the required format.""",
            contexts_list=results
        )

        # Step 5: Final Validation
        validated_solution = await self.revise(
            instruction="""Verify the final solution:
            - Check numerical accuracy.
            - Ensure logical consistency.
            - Confirm alignment with the problem's constraints.""",
            context=final_solution
        )

        return validated_solution