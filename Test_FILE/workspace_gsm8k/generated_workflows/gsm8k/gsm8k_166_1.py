# Workflow ID: gsm8k_166_1
# Benchmark: gsm8k
# Data Indices: [821, 467, 545]

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
        This is a diverse and effective workflow using the 'Reflect and Regenerate' pattern.
        It first generates an initial solution, then critically reflects on it to identify potential flaws or improvements.
        Finally, it uses that reflection to guide a new, improved solution — mimicking human meta-cognition.
        This approach ensures deep reasoning by incorporating self-awareness before finalizing the answer.
        """
        # Step 1: Generate an initial solution with clear, structured instructions
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Break down the problem into smaller parts."
        )

        # Step 2: Critically reflect on the initial solution — do not rewrite it yet
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined, higher-quality solution
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses any issues or gaps identified in the reflection."
        )

        return final_solution