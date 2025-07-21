# Workflow ID: gsm8k_102_0
# Benchmark: gsm8k
# Data Indices: [481, 820]

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
        This is a diverse and efficient workflow using iterative refinement with reflection.
        It starts with a structured approach (FlexibleCustom), then reflects on the result,
        and finally uses that reflection to guide a final custom solution — all in under 6 steps.
        """
        # Step 1: Use FlexibleCustom with an iterative reasoning pattern to generate a solid initial solution
        initial_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve the problem by breaking it into clear steps: identify what's given, determine what needs to be found, apply relevant operations, and verify the logic."
        )

        # Step 2: Reflect critically on the solution — look for assumptions, errors, or missing logic
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final improved solution based on the reflection
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. Now, provide a corrected and more robust answer. Be precise and ensure all steps are logically sound."
        )

        return final_solution