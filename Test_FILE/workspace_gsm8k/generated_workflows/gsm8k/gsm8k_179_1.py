# Workflow ID: gsm8k_179_1
# Benchmark: gsm8k
# Data Indices: [538, 923]

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
        then uses that reflection to guide a new, improved solution — mimicking human metacognition.
        """

        # Step 1: Generate an initial solution using flexible custom reasoning (sequential approach)
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning.",
            reasoning_pattern="sequential",
            steps=["understand", "break_down", "compute", "verify"]
        )

        # Step 2: Critically reflect on the initial solution — identify potential flaws, oversights, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined, higher-quality solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Reconstruct the solution to address these points. Provide a detailed, accurate answer."
        )

        return final_answer