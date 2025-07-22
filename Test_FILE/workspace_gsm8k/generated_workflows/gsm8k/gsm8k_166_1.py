# Workflow ID: gsm8k_166_1
# Benchmark: gsm8k
# Data Indices: [168, 660, 851]

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
        1. Generate 3 independent solutions using parallel reasoning (Fan-out).
        2. Use ScEnsemble to select the best solution.
        3. Reflect on that best solution to identify potential flaws or missed angles.
        4. Regenerate a final solution informed by the reflection — this mimics meta-cognitive learning.
        
        This approach combines robustness (parallel) with deep refinement (reflection), avoiding single-point failure and enabling self-improvement.
        """

        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction=f"Approach the problem from a different angle than the others. Be precise and show all steps. Solution {i+1} of 3."
            )
            solution_candidates.append(candidate)

        # Step 2: Select the most accurate solution using ensemble evaluation
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the best solution — don't fix it yet
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the previous solution:\n\n{reflection}\n\nRevise the solution accordingly to address any overlooked assumptions, logical gaps, or alternative interpretations. Provide a fully revised answer."
        )

        return final_solution