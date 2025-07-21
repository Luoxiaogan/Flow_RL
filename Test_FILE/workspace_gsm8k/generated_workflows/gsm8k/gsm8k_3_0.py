# Workflow ID: gsm8k_3_0
# Benchmark: gsm8k
# Data Indices: [945, 267]

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
        This is a diverse workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it,
        and finally uses that reflection to guide a new, improved solution.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying what is given and what needs to be found.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"]
        )

        # Step 2: Critically reflect on the initial solution to uncover potential flaws or missed steps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution — this is the core of the Reflect-and-Regenerate loop
        final_solution = await self.custom(
            instruction=f"Given the following initial solution and reflection: '{reflection}'. "
                        f"Re-solve the problem with improved clarity, ensuring all assumptions are valid "
                        f"and all steps are logically sound."
        )

        return final_solution