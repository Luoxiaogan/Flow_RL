# Workflow ID: gsm8k_60_1
# Benchmark: gsm8k
# Data Indices: [194, 113]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        Diverse and efficient workflow using Iterative Refinement (Review-based).
        This structure applies progressive improvement through two rounds of Review,
        ensuring the solution is polished step-by-step — a fundamentally different logic from the original.
        """

        # Step 1: Generate an initial solution with minimal reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into clear steps. Be concise."
        )

        # Step 2: Apply first refinement via Review — improves clarity and correctness
        refined_solution_1 = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second refinement via Review — addresses deeper issues missed in first pass
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        # Step 4: Final output — return the most improved version after iterative review
        return refined_solution_2