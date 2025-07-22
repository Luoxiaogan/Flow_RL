# Workflow ID: gsm8k_280_0
# Benchmark: gsm8k
# Data Indices: [271, 973, 236]

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
        2. Select the best one using ScEnsemble.
        3. Reflect on it to identify potential flaws or improvements.
        4. Use that reflection to guide a new Custom call for final refinement.
        This ensures both robustness (from ensemble) and meta-cognition (from reflection).
        """
        # Step 1: Generate multiple solutions in parallel (Fan-out)
        solution_candidates = []
        for _ in range(3):
            candidate = await self.custom(
                instruction="Solve the problem step-by-step, explaining your reasoning clearly. Focus on clarity and logical flow."
            )
            solution_candidates.append(candidate)

        # Step 2: Evaluate and select the best solution (Fan-in)
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the selected solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new custom generation for final improvement
        final_answer = await self.custom(
            instruction=f"Given the following initial solution and reflection: {reflection}. Now, provide a refined, improved version of the solution based on this critique."
        )

        return final_answer