# Workflow ID: gsm8k_285_0
# Benchmark: gsm8k
# Data Indices: [764, 86, 182]

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
        It uses a single initial solution, reflects on it to identify potential blind spots,
        then generates an improved solution based on that reflection — all in under 5 steps.
        """
        # Step 1: Generate an initial solution using flexible custom with a sequential reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, breaking it into clear logical parts.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "execute", "verify"]
        )

        # Step 2: Reflect critically on the initial solution to uncover assumptions or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted solution generation
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, solve the problem again with more precision and attention to detail."
        )

        return final_solution