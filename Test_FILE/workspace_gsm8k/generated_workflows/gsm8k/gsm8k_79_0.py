# Workflow ID: gsm8k_79_0
# Benchmark: gsm8k
# Data Indices: [797, 551]

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
        This is a diverse and efficient workflow using iterative refinement with reflection.
        It leverages the Reflect operator to critique an initial solution, then uses that insight
        to guide a new, improved solution — a meta-cognitive loop for higher accuracy without unnecessary complexity.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(instruction="Solve the problem by breaking it into logical steps: identify knowns, apply formulas, compute results, and verify units.")

        # Step 2: Critically reflect on the initial solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted instruction for a refined solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. Now, solve the problem again with improved clarity and correctness, ensuring all steps are logically sound and unit-consistent."
        )

        return final_solution