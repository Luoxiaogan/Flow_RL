# Workflow ID: gsm8k_104_0
# Benchmark: gsm8k
# Data Indices: [393, 743]

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
        A diverse and efficient workflow using iterative refinement with reflection.
        This structure balances simplicity and effectiveness by first generating a solution,
        then reflecting on it to uncover potential blind spots, and finally regenerating
        a more robust answer based on that insight — all in under 6 steps.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using clear logical reasoning.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Reflect on the initial solution to identify possible flaws or missed details
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be precise and thorough."
        )

        return final_solution