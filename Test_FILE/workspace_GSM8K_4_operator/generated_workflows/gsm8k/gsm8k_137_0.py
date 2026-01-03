# Workflow ID: gsm8k_137_0
# Benchmark: gsm8k
# Data Indices: [141, 128]

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

        # Phase 1: Initial Analysis
        analysis = await self.generate(
            instruction="""Extract key information and classify the problem:
            - Identify all numerical values and their context
            - Determine relationships between entities
            - Classify the problem type (numerical, rate, distribution, proportion)
            - Highlight any constraints or conditions
            Provide a structured breakdown.""",
            context=""
        )

        # Phase 2: Strategy Selection
        if "rate" in analysis.lower():
            strategy = "dimensional_analysis"
        elif "distribution" in analysis.lower():
            strategy = "modular_arithmetic"
        else:
            strategy = "precise_computation"

        # Phase 3: Parallel Exploration
        async def explore_approach(approach):
            return await self.generate(
                instruction=f"""Solve the problem using {approach}:
                - Show all intermediate steps
                - Maintain numerical precision
                - Validate results against constraints""",
                context=analysis
            )

        approaches = ["algebraic", "estimation", strategy]
        results = await asyncio.gather(*[explore_approach(a) for a in approaches])

        # Phase 4: Iterative Refinement
        refined_result = results[0]  # Start with one result
        for _ in range(3):  # Allow up to 3 refinement iterations
            validation = await self.generate(
                instruction="Validate the solution for correctness and consistency.",
                context=refined_result
            )
            if "error" in validation.lower():
                refined_result = await self.revise(
                    instruction=f"Correct errors based on validation: {validation}",
                    context=refined_result
                )
            else:
                break

        # Phase 5: Final Synthesis
        final_answer = await self.summarize(
            instruction="Condense the solution into a single numerical answer.",
            context=refined_result
        )

        return final_answer