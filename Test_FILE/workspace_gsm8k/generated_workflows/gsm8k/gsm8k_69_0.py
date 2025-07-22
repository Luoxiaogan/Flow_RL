# Workflow ID: gsm8k_69_0
# Benchmark: gsm8k
# Data Indices: [528, 799, 240]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Critically reflect on it to identify potential flaws or improvements.
        4. Use that reflection to guide a new Custom call for a refined final answer.
        This structure mimics human meta-cognition: try multiple approaches, pick the best, then refine it with insight.
        """

        # Step 1: Generate multiple candidate solutions in parallel (Fan-out)
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step, explaining your reasoning clearly. Focus on clarity, correctness, and logical flow."
            )
            solution_candidates.append(candidate)

        # Step 2: Evaluate and select the best solution (Fan-in)
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the selected solution (Meta-cognitive step)
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a targeted re-generation of the solution
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection:\n{reflection}\n\nNow, provide a revised and improved solution based on this reflection. Ensure all steps are logically sound and clearly explained."
        )

        return final_answer