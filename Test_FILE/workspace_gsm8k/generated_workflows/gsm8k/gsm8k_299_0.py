# Workflow ID: gsm8k_299_0
# Benchmark: gsm8k
# Data Indices: [871, 203]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions using parallel approach.
        Step 2: Select best solution via ScEnsemble.
        Step 3: Reflect on the selected solution to uncover potential flaws or improvements.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- Phase 1: Parallel Ensemble ---
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(instruction="Solve the problem step-by-step, breaking it into logical parts. Be precise and avoid assumptions.")
            solution_candidates.append(candidate)

        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- Phase 2: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Phase 3: Regenerate Based on Reflection ---
        # Use FlexibleCustom in iterative mode to refine the solution based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Improve the solution below using this reflection: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze", "refine", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution