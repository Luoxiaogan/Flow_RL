# Workflow ID: gsm8k_125_0
# Benchmark: gsm8k
# Data Indices: [51, 921, 189]

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
        This is a diverse and reflective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to produce a refined, higher-quality answer.
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each calculation clearly."
        )

        # Step 2: Critically reflect on the solution — identify potential flaws, assumptions, or missed steps
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Re-solve the problem by addressing any weaknesses identified. Ensure your reasoning is thorough and logically sound."
        )

        return final_solution