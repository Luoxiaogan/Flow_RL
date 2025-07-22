# Workflow ID: gsm8k_127_1
# Benchmark: gsm8k
# Data Indices: [538, 405, 592]

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
        This is a novel workflow using Iterative Refinement with FlexibleCustom.
        1. Use FlexibleCustom in iterative mode to generate an initial solution and refine it over 2 passes.
        2. If the refined solution still seems questionable (based on reflection), apply one final review.
        This avoids parallelism entirely and focuses on progressive improvement — a different logic from the original ensemble+reflect pattern.
        """

        # Step 1: Use iterative FlexibleCustom for structured refinement
        flexible_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step with clear reasoning.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the final iterative solution to catch any lingering issues
        reflection = await self.reflect(pre_solution=flexible_solution)

        # Step 3: Only if reflection suggests problems, do a single final review pass
        if "error" in reflection.lower() or "assumption" in reflection.lower() or "improve" in reflection.lower():
            final_solution = await self.review(pre_solution=flexible_solution)
        else:
            final_solution = flexible_solution

        return final_solution