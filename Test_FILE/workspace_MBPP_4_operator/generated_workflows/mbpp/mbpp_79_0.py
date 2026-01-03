# Workflow ID: mbpp_79_0
# Benchmark: mbpp
# Data Indices: [265]

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

        # Phase 1: Problem Analysis
        analysis = await self.generate(
            instruction="""Extract key components from the problem:
            1. Function name from assert statements.
            2. Input types and expected behavior.
            3. Any implicit constraints or edge cases.
            Provide structured output.""",
            context=""
        )

        # Phase 2: Solution Exploration
        # Generate multiple candidate solutions in parallel
        candidates = await asyncio.gather(
            self.generate(
                instruction=f"""Generate a solution focusing on straightforward logic:
                {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution using Python standard library functions:
                {analysis}""",
                context=analysis
            ),
            self.generate(
                instruction=f"""Generate a solution considering edge cases:
                {analysis}""",
                context=analysis
            )
        )

        # Phase 3: Validation and Refinement
        # Summarize candidates for ensemble decision
        summary = await self.summarize(
            instruction="Condense candidate solutions into key approaches.",
            context="\n".join(candidates)
        )

        # Select the best solution or synthesize a hybrid
        best_solution = await self.ensemble(
            instruction="Choose the most robust and accurate solution.",
            contexts_list=candidates
        )

        # Refine the selected solution
        refined_solution = await self.revise(
            instruction="Ensure the solution passes all test cases and adheres to Python syntax.",
            context=best_solution
        )

        # Final Output
        return refined_solution