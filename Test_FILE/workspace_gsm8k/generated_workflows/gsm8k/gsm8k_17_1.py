# Workflow ID: gsm8k_17_1
# Benchmark: gsm8k
# Data Indices: [89, 476]

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
        This is a diverse and robust workflow using the Iterative Refinement pattern.
        Generates an initial solution, then applies Review twice to progressively improve it.
        This mimics human-like iterative thinking: solve → critique → refine → critique again → finalize.
        """

        # --- Step 1: Generate an initial solution with clear step-by-step reasoning ---
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into logical steps. Explain each step as if teaching someone who is learning math for the first time."
        )

        # --- Step 2: First refinement via Review — improve clarity, fix obvious errors ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement via Review — deepen accuracy, ensure consistency ---
        second_refined = await self.review(pre_solution=first_refined)

        # --- Step 4: Final output — return the most refined version after two rounds of review ---
        final_answer = second_refined

        return final_answer