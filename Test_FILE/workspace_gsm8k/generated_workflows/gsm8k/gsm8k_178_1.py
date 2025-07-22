# Workflow ID: gsm8k_178_1
# Benchmark: gsm8k
# Data Indices: [362, 436, 243]

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
        This workflow uses a Reflect-and-Regenerate pattern with minimal steps for maximum efficiency.
        It first generates an initial solution, reflects on it to uncover hidden assumptions or errors,
        then uses that reflection to guide a targeted re-solution — all in just 3 core steps.
        This is logically distinct from the existing workflow's parallel ensemble strategy.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, focusing on clear logic and explicit calculations.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: Critically reflect on the solution to identify potential flaws or missed details
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined, more accurate final answer
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}', revise your solution to address any identified issues. Provide only the final, corrected answer."
        )

        return final_answer