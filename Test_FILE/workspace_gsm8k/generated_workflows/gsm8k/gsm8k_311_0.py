# Workflow ID: gsm8k_311_0
# Benchmark: gsm8k
# Data Indices: [338, 731, 977]

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
        It uses Reflect to identify potential flaws in the initial solution, then guides a refined approach.
        This pattern balances simplicity with meta-cognitive improvement—ideal for efficiency and robustness.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining each reasoning step clearly.")

        # Step 2: Critically reflect on the solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. "
                        "Now, re-solve the problem by addressing the identified issues. Be precise and systematic."
        )

        return final_solution