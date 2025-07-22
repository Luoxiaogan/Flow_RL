# Workflow ID: gsm8k_66_0
# Benchmark: gsm8k
# Data Indices: [867, 153]

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
        and finally uses that insight to generate a refined solution — all in under 6 steps.
        """
        # Step 1: Use FlexibleCustom with an iterative reasoning pattern for systematic breakdown
        initial_solution = await self.flexible_custom(
            custom_instruction="Apply a step-by-step method to solve math problems",
            reasoning_pattern="iterative",
            steps=["understand", "formulate", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the initial solution to uncover potential blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final improved solution based on reflection
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial attempt: '{reflection}'. "
                        f"Refine your solution accordingly. Be precise and logical."
        )

        return final_solution