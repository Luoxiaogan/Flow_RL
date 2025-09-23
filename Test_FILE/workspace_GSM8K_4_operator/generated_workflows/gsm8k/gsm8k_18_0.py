# Workflow ID: gsm8k_18_0
# Benchmark: gsm8k
# Data Indices: [218, 12]

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

        # Step 1: Initial Analysis - Extract key information and classify problem
        initial_analysis = await self.generate(
            instruction="""Extract all numerical values, units, and relationships in the problem.
            Classify the problem type (e.g., rate, distribution, proportion).
            Identify the goal of the problem (e.g., remaining money, age, distance).
            Format the output as structured text.""",
            context=""
        )

        # Step 2: Parallel Exploration - Generate multiple solution strategies
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using the initial analysis: {initial_analysis}
                Develop a solution strategy focusing on sequential operations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis: {initial_analysis}
                Develop a solution strategy focusing on rate calculations.""",
                context=initial_analysis
            ),
            self.generate(
                instruction=f"""Using the initial analysis: {initial_analysis}
                Develop a solution strategy focusing on proportions and scaling.""",
                context=initial_analysis
            )
        )

        # Step 3: Validation and Refinement - Critique and improve each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Validate and refine this solution strategy. Ensure all steps are accurate and logical.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Ensemble Decision - Select the best strategy
        final_strategy = await self.ensemble(
            instruction="Evaluate these strategies and select the most accurate and logical one.",
            contexts_list=refined_strategies
        )

        # Step 5: Iterative Feedback - Refine the final strategy if necessary
        for _ in range(2):  # Allow up to 2 iterations for refinement
            validation = await self.generate(
                instruction="Validate the final strategy. Identify any errors or areas for improvement.",
                context=final_strategy
            )
            if "error" in validation.lower():
                final_strategy = await self.revise(
                    instruction=f"Fix issues identified in validation: {validation}",
                    context=final_strategy
                )
            else:
                break

        # Step 6: Extract Final Answer
        final_answer = await self.generate(
            instruction="From the final strategy, extract the numerical answer in the required format.",
            context=final_strategy
        )

        return final_answer