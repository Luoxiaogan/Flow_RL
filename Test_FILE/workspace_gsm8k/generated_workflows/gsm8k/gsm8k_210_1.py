# Workflow ID: gsm8k_210_1
# Benchmark: gsm8k
# Data Indices: [902, 743]

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
        This is a diverse and efficient workflow using the Reflect-and-Regenerate pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws or improvements,
        and finally uses that reflection to guide a new, targeted custom reasoning step — ensuring meta-cognitive depth without unnecessary complexity.
        """

        # Step 1: Generate an initial solution using general-purpose step-by-step breakdown
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into clear, logical steps. Show all calculations explicitly."
        )

        # Step 2: Use Reflect to critique the solution — not to fix it, but to uncover assumptions, gaps, or alternative paths
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to inform a focused, improved solution via Custom
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        "Now solve the problem again with deeper insight, addressing any weaknesses identified."
        )

        return final_answer