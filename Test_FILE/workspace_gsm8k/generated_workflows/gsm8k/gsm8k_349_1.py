# Workflow ID: gsm8k_349_1
# Benchmark: gsm8k
# Data Indices: [45, 205, 614]

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
        It starts with an initial solution, then applies two rounds of Review to progressively improve it.
        This mimics how humans refine their thinking through multiple passes—first identifying errors, then improving clarity and accuracy.
        """
        # --- Step 1: Generate an initial solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # --- Step 2: First refinement via Review ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement via Review (further polish) ---
        second_refined = await self.review(pre_solution=first_refined)

        # --- Optional: Final reflection for meta-cognitive insight (not used in this logic but could be added if needed) ---
        # reflection = await self.reflect(pre_solution=second_refined)

        return second_refined