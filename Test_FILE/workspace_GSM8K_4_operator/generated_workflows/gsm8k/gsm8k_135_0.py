# Workflow ID: gsm8k_135_0
# Benchmark: gsm8k
# Data Indices: [140, 86]

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

        # Step 1: Initial Analysis - Extract key information and classify the problem
        initial_analysis = await self.generate(
            instruction="""Analyze the problem thoroughly:
            - Identify all numerical values and their units.
            - Extract entities (people, objects, etc.) and their relationships.
            - Classify the problem type (rate, distribution, proportion, etc.).
            - Determine what the problem is asking for.
            Provide structured output with clear categories.""",
            context=""
        )

        # Step 2: Generate Multiple Solution Paths in Parallel
        solution_paths = await asyncio.gather(
            self.generate(
                instruction=f"""Propose a solution path using a sequential calculation approach:
                Problem analysis: {initial_analysis}
                - Break the problem into small steps.
                - Perform calculations step-by-step.
                - Show intermediate results clearly.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Propose a solution path using a proportional reasoning approach:
                Problem analysis: {initial_analysis}
                - Identify proportional relationships.
                - Use ratios, fractions, or percentages as needed.
                - Show intermediate results clearly.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Propose a solution path using a unit-based approach:
                Problem analysis: {initial_analysis}
                - Focus on units and conversions.
                - Ensure dimensional consistency throughout.
                - Show intermediate results clearly.""",
                context=initial_analysis
            )
        )

        # Step 3: Validate and Refine Each Path Independently
        refined_paths = await asyncio.gather(
            *[self.revise(
                instruction=f"""Refine the solution path:
                - Check for calculation errors.
                - Ensure logical consistency.
                - Clarify ambiguous steps.""",
                context=path
            ) for path in solution_paths]
        )

        # Step 4: Synthesize and Select the Best Path
        final_solution = await self.ensemble(
            instruction="""Compare the refined solution paths:
            - Evaluate accuracy and completeness.
            - Check adherence to problem constraints.
            - Select the most robust and efficient path.""",
            contexts_list=refined_paths
        )

        # Step 5: Compute the Final Answer
        final_answer = await self.generate(
            instruction=f"""Compute the final answer:
            Selected solution path: {final_solution}
            - Perform the final calculation step.
            - Ensure the result matches the required format (numerical value).""",
            context=final_solution
        )

        return final_answer