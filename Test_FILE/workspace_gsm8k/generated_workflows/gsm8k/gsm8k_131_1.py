# Workflow ID: gsm8k_131_1
# Benchmark: gsm8k
# Data Indices: [30, 984, 930]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        1. Generate 3 independent solutions via parallel approach (using FlexibleCustom in 'parallel' mode).
        2. Use ScEnsemble to select the best candidate.
        3. Critically reflect on that solution using the new Reflect operator.
        4. Regenerate a final answer based on reflection — this ensures meta-cognitive improvement.
        
        This design combines two distinct patterns:
        - Parallel Ensemble (fan-out/fan-in) for robustness against reasoning errors
        - Reflect-and-Regenerate for deeper insight and refinement beyond surface-level fixes
        
        Unlike the existing workflow (which uses iterative review), this one leverages diversity first, then introspection.
        """
        # Step 1: Generate multiple solutions in parallel using FlexibleCustom with 'parallel' pattern
        parallel_solutions = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem systematically.",
                reasoning_pattern="parallel",
                steps=["understand", "analyze", "compute", "verify"]
            )
            parallel_solutions.append(solution)

        # Step 2: Select the best solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # Step 3: Reflect critically on the selected solution—identify potential flaws or missed angles
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new, improved Custom call—not just fixing but rethinking
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Now, solve the problem again with a fresh perspective, ensuring all assumptions are valid and no steps were skipped."
        )

        return final_answer