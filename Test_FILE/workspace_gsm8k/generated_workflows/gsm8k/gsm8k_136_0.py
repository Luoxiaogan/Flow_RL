# Workflow ID: gsm8k_136_0
# Benchmark: gsm8k
# Data Indices: [864, 341]

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
        It generates an initial solution, reflects on it to uncover potential blind spots,
        then uses that reflection to guide a targeted improvement — all in under 5 steps.
        """
        # Step 1: Generate an initial solution with clear step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into smaller steps. Show each calculation clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a focused custom instruction for refinement
        refined_instruction = f"Based on the following reflection:\n{reflection}\n\nRe-solve the problem with improved clarity and accuracy. Pay special attention to any overlooked details."

        # Step 4: Generate a final, improved solution using the reflection-guided instruction
        final_solution = await self.custom(instruction=refined_instruction)

        return final_solution