# Workflow ID: gsm8k_139_1
# Benchmark: gsm8k
# Data Indices: [957, 696, 187]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best one using ScEnsemble.
        3. Reflect on the selected solution to identify potential blind spots or assumptions.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        This combines robustness (parallel) with meta-cognition (reflection) and targeted improvement (iterative).
        """
        # Step 1: Generate multiple independent solutions (Parallel Ensemble)
        solutions = []
        for i in range(3):
            sol = await self.flexible_custom(
                custom_instruction="Approach the problem from a different perspective each time.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solutions.append(sol)

        # Step 2: Evaluate and select the best solution
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the chosen solution to uncover hidden issues
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution informed by the reflection
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Improve the solution by addressing potential flaws or missed assumptions.",
            reasoning_pattern="iterative",
            steps=["identify_weaknesses", "refine_approach", "recompute"],
            max_iterations=2
        )

        return final_solution