# Workflow ID: limr_103_0
# Benchmark: limr
# Data Indices: [77, 168]

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
            instruction="""Analyze the problem thoroughly. Identify its type (geometry, number theory, etc.), 
            key variables, constraints, and relationships. Suggest potential solution strategies.""",
            context=""
        )

        # Step 2: Parallel Exploration
        strategies = ["analytical", "numerical", "heuristic"]
        explorations = await asyncio.gather(
            *[self.generate(
                instruction=f"Develop a detailed solution using {strategy} approach. "
                            f"Include all steps, assumptions, and intermediate results.",
                context=initial_analysis
            ) for strategy in strategies]
        )

        # Step 3: Validation and Refinement
        refined_solutions = await asyncio.gather(
            *[self.revise(
                instruction="Review the solution for logical consistency, calculation accuracy, and completeness. "
                            "Correct errors and fill gaps in reasoning.",
                context=solution
            ) for solution in explorations]
        )

        # Step 4: Synthesis and Selection
        final_solution = await self.ensemble(
            instruction="Compare all solutions. Select the most rigorous and complete one. "
                        "If multiple solutions are valid, synthesize them into a unified answer.",
            contexts_list=refined_solutions
        )

        # Step 5: Final Verification
        verified_solution = await self.generate(
            instruction="Verify the final solution against the original problem. "
                        "Ensure it satisfies all constraints and matches the expected format.",
            context=final_solution
        )

        return verified_solution