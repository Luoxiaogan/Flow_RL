# Workflow ID: gsm8k_173_0
# Benchmark: gsm8k
# Data Indices: [928, 856, 808]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Reflect on that solution to uncover potential flaws or missed angles.
        4. Use reflection to guide a targeted regen of the solution with FlexibleCustom in iterative mode.
        """

        # Step 1: Generate multiple candidate solutions (Parallel Ensemble pattern)
        solutions = []
        for _ in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step, explaining your reasoning clearly. Be thorough and precise.")
            solutions.append(sol)

        # Step 2: Enforce quality control — pick the best among them
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critical reflection — analyze the chosen solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Conditional regeneration based on reflection — if reflection suggests improvement is possible, refine iteratively
        if "incomplete" in reflection.lower() or "assumption" in reflection.lower() or "missing" in reflection.lower():
            # Use FlexibleCustom in iterative mode to refine the solution
            refined_solution = await self.flexible_custom(
                custom_instruction="Based on the following reflection, improve the solution: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "adjust_approach", "recompute"],
                max_iterations=2,
                use_structured_output=True
            )
            return refined_solution
        else:
            # If no major flaws found, return the original best solution
            return best_solution