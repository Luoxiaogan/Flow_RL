# Workflow ID: gsm8k_189_0
# Benchmark: gsm8k
# Data Indices: [610, 482]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This approach uses reflection to guide iterative improvement — a meta-cognitive loop.
        It's simple (only 3 steps), logical, and avoids unnecessary complexity.
        """
        # Step 1: Initial solution via flexible custom with iterative reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "execute", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the solution — identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to generate a final improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem carefully, incorporating these insights to avoid errors."
        )

        return final_solution