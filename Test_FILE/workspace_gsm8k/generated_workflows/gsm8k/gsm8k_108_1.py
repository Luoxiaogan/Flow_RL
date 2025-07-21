# Workflow ID: gsm8k_108_1
# Benchmark: gsm8k
# Data Indices: [342, 861]

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
        This is a diverse and robust workflow using the 'Reflect and Regenerate' pattern.
        It generates an initial solution, critically reflects on it to uncover hidden assumptions or errors,
        then uses that reflection to guide a targeted re-solution. This meta-cognitive loop ensures high-quality reasoning.
        """
        # Step 1: Generate an initial solution with a general instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Focus on identifying all components before calculating totals."
        )

        # Step 2: Critically reflect on the initial solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a new, improved solution that addresses any weaknesses identified in the reflection."
        )

        return final_answer