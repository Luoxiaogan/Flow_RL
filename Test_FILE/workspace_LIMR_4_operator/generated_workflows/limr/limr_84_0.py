# Workflow ID: limr_84_0
# Benchmark: limr
# Data Indices: [51, 192]

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
            instruction="""Analyze the problem thoroughly:
            - Identify the mathematical domain (e.g., algebra, geometry).
            - Extract all variables, equations, and constraints.
            - Determine potential solution strategies.
            Provide a structured summary.""",
            context=""
        )

        # Step 2: Solution Exploration (Parallel Strategies)
        strategies = await asyncio.gather(
            self.generate(
                instruction="Attempt an algebraic solution, focusing on symbolic manipulation.",
                context=analysis
            ),
            self.generate(
                instruction="Attempt a geometric interpretation, visualizing relationships.",
                context=analysis
            ),
            self.generate(
                instruction="Attempt a combinatorial approach, enumerating possibilities.",
                context=analysis
            ),
            self.generate(
                instruction="Attempt an optimization strategy, finding maxima/minima.",
                context=analysis
            )
        )

        # Step 3: Refinement and Validation
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction=f"Refine and validate this solution: {solution}",
                context=solution
            ) for solution in strategies]
        )

        # Step 4: Synthesis and Decision
        final_solution = await self.ensemble(
            instruction="""Synthesize the refined solutions:
            - Compare their validity and completeness.
            - Resolve any conflicts or inconsistencies.
            - Ensure the final answer is an integer between 000 and 999.
            Select the best solution.""",
            contexts_list=refined_solutions
        )

        # Step 5: Iterative Improvement (Optional)
        validation = await self.generate(
            instruction="Validate the final solution against the original problem.",
            context=final_solution
        )
        if "error" in validation.lower():
            final_solution = await self.revise(
                instruction=f"Fix issues identified in validation: {validation}",
                context=final_solution
            )

        return final_solution