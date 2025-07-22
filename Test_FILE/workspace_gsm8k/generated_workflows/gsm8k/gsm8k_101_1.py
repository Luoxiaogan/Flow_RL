# Workflow ID: gsm8k_101_1
# Benchmark: gsm8k
# Data Indices: [305, 252]

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
        It generates an initial solution, critically reflects on it to uncover hidden assumptions or errors,
        then uses that reflection to guide a targeted revision — mimicking human metacognition.
        This approach avoids unnecessary parallelism or ensembling, focusing instead on quality of reasoning.
        """
        # Step 1: Generate initial solution with clear step-by-step instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each reasoning step clearly."
        )

        # Step 2: Critically reflect on the solution — identify potential flaws, missing steps, or alternative interpretations
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a new, improved solution tailored to address the identified issues
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        "Now, provide a revised solution that addresses the concerns raised in the reflection."
        )

        return final_answer