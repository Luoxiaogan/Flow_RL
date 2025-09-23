# Workflow ID: gsm8k_90_0
# Benchmark: gsm8k
# Data Indices: [49, 2]

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

        # Step 1: Extract key information and classify the problem
        problem_analysis = await self.generate(
            instruction="""Extract all numerical values, entities, and relationships from the problem.
            Classify the problem type (e.g., sequential operations, proportions, rate problems).
            Identify what the question asks for and any constraints.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"Propose a sequential solution strategy based on: {problem_analysis}",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"Propose a proportional reasoning strategy based on: {problem_analysis}",
                context=problem_analysis
            ),
            self.generate(
                instruction=f"Propose a rate-based solution strategy based on: {problem_analysis}",
                context=problem_analysis
            )
        )

        # Step 3: Validate and refine strategies
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction="Validate calculations and logical consistency. Address any gaps or errors.",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Select the best strategy using ensemble
        best_strategy = await self.ensemble(
            instruction="Select the most accurate and efficient strategy. Prioritize clarity and correctness.",
            contexts_list=refined_strategies
        )

        # Step 5: Execute the selected strategy step-by-step
        solution_steps = await self.generate(
            instruction=f"Execute the selected strategy step-by-step: {best_strategy}. Show all intermediate results.",
            context=best_strategy
        )

        # Step 6: Validate the final solution
        final_validation = await self.revise(
            instruction="Verify the final answer against the problem's requirements. Ensure numerical precision.",
            context=solution_steps
        )

        # Step 7: Extract and return the final numerical answer
        final_answer = await self.summarize(
            instruction="Extract the final numerical answer from the solution. Format as a single number.",
            context=final_validation
        )

        return final_answer.strip()