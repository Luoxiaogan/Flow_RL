# Workflow ID: gsm8k_324_1
# Benchmark: gsm8k
# Data Indices: [759, 832]

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
        This is a diverse and robust workflow using the Reflect and Regenerate pattern.
        It first generates an initial solution, critically reflects on it to uncover potential flaws or improvements,
        then uses that reflection to guide a targeted regeneration of the final answer.
        This meta-cognitive loop ensures deeper reasoning than a single pass.
        """

        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Be explicit about each calculation."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, missing logic, or possible errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution — this is the key difference from the existing workflow
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        "Now, provide a revised and improved solution that addresses the points raised in the reflection."
        )

        return final_answer