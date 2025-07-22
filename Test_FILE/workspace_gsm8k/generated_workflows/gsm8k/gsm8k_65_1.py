# Workflow ID: gsm8k_65_1
# Benchmark: gsm8k
# Data Indices: [757, 671, 379]

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
        It generates an initial solution, critically reflects on its potential flaws or assumptions,
        and then uses that reflection to guide a new, improved solution — mimicking meta-cognitive reasoning.
        This approach prioritizes deep understanding over brute-force ensembling.
        """

        # Step 1: Generate an initial solution using general-purpose reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not assume any prior knowledge."
        )

        # Step 2: Critically reflect on the solution — identify hidden assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # Step 3: Use the reflection to craft a targeted instruction for a refined solution
        improved_instruction = (
            f"Given the following initial solution: {initial_solution}\n\n"
            f"And this reflection on its limitations: {reflection}\n\n"
            "Now, provide a revised solution that addresses these points explicitly."
        )

        # Step 4: Generate the final answer based on the reflective critique
        final_answer = await self.custom(instruction=improved_instruction)

        return final_answer