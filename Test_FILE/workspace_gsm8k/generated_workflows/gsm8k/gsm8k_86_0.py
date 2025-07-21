# Workflow ID: gsm8k_86_0
# Benchmark: gsm8k
# Data Indices: [790, 57]

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
        Diverse and efficient workflow using iterative refinement with reflection.
        This pattern combines meta-cognition (reflection) with iterative improvement.
        It's simple yet effective—only 4 operators—but leverages deeper reasoning.
        """
        # Step 1: Initial solution using structured sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem systematically.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Reflect on the solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use reflection to guide a refined custom response
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. "
                        f"Re-solve the problem with improved clarity and accuracy."
        )

        return final_solution