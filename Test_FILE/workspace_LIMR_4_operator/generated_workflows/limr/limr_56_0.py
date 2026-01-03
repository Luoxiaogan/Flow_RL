# Workflow ID: limr_56_0
# Benchmark: limr
# Data Indices: [137, 143]

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

        # Step 1: Classify the problem and extract key components
        classification = await self.generate(
            instruction="""Classify this problem into one of the following categories:
            - Geometry (e.g., 3D shapes, coordinate transformations)
            - Number Theory (e.g., modular arithmetic, primes)
            - Combinatorics (e.g., counting, probability)
            - Algebra (e.g., polynomials, equations)
            - Optimization (e.g., maxima/minima, inequalities)
            Also, identify key components such as variables, constraints, and goals.""",
            context=""
        )

        # Step 2: Generate multiple solution strategies in parallel
        strategies = await asyncio.gather(
            self.generate(
                instruction=f"""Using a direct approach, solve the problem step-by-step.
                Classification: {classification}
                Show all calculations and reasoning.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using a transformative approach, apply creative insights to simplify the problem.
                Classification: {classification}
                Consider substitutions, symmetries, or alternative representations.""",
                context=classification
            ),
            self.generate(
                instruction=f"""Using a verification approach, cross-check the problem's constraints and conditions.
                Classification: {classification}
                Ensure all steps are logically consistent.""",
                context=classification
            )
        )

        # Step 3: Refine and validate each strategy
        refined_strategies = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate this solution attempt: {strategy}",
                context=strategy
            ) for strategy in strategies]
        )

        # Step 4: Summarize key insights from each strategy
        summaries = await asyncio.gather(
            *[self.summarize(
                instruction=f"Condense this solution attempt into key insights: {strategy}",
                context=strategy
            ) for strategy in refined_strategies]
        )

        # Step 5: Ensemble to select the best solution or synthesize insights
        final_solution = await self.ensemble(
            instruction="""Evaluate these solution attempts and select the best one.
            Criteria:
            - Logical consistency
            - Precision and correctness
            - Alignment with problem requirements""",
            contexts_list=summaries
        )

        return final_solution