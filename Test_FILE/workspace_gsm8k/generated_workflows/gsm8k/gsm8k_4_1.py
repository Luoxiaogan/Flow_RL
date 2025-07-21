# Workflow ID: gsm8k_4_1
# Benchmark: gsm8k
# Data Indices: [91, 654]

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
        It generates an initial solution, critically reflects on its potential flaws or assumptions,
        and then uses that reflection to guide a more precise and improved final solution.
        This mimics human metacognition: solving → evaluating → improving.
        """

        # --- Step 1: Generate an initial solution using flexible custom reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into logical steps and explaining your reasoning clearly.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # --- Step 2: Critically reflect on the initial solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to generate a refined, higher-quality solution ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        f"Now, provide a new, improved solution that addresses any weaknesses or ambiguities identified in the reflection."
        )

        return final_answer