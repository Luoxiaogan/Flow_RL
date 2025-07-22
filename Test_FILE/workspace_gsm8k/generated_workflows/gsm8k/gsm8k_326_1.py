# Workflow ID: gsm8k_326_1
# Benchmark: gsm8k
# Data Indices: [945, 631]

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
        Diverse workflow using parallel ensemble with iterative refinement — a fundamentally different logic from the existing one.
        This approach first generates multiple candidate solutions in parallel (fan-out), then uses iterative refinement on the best one (fan-in).
        It avoids single-point failure by leveraging diversity upfront and improves robustness through targeted iteration.
        """
        # Step 1: Generate 3 independent solutions in parallel using Custom
        solution1 = await self.custom(instruction="Solve step-by-step with clear reasoning.")
        solution2 = await self.custom(instruction="Break down the problem into smaller steps and solve each systematically.")
        solution3 = await self.custom(instruction="Apply structured reasoning: identify knowns, unknowns, and required operations.")

        # Step 2: Use ScEnsemble to select the best among them
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Refine the best solution iteratively using Review
        refined_solution = await self.review(pre_solution=best_solution)

        return refined_solution