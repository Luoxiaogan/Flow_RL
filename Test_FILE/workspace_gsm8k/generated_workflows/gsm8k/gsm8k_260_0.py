# Workflow ID: gsm8k_260_0
# Benchmark: gsm8k
# Data Indices: [951, 838]

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
        Diverse workflow combining Parallel Ensemble + Reflect and Regenerate.
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select best solution using ScEnsemble.
        3. Reflect on the selected solution to uncover hidden flaws or assumptions.
        4. Use reflection to guide a new, improved Custom call for final answer.
        This creates a meta-cognitive loop that enhances accuracy without overfitting.
        """

        # Step 1: Generate multiple candidate solutions (Parallel Ensemble)
        candidates = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step with clear reasoning. Focus on identifying key variables and relationships."
            )
            candidates.append(solution)

        # Step 2: Choose the best solution using ensemble evaluation
        best_solution = await self.sc_ensemble(solutions=candidates)

        # Step 3: Critically reflect on the best solution (no rewrite yet)
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new, targeted custom generation
        final_answer = await self.custom(
            instruction=f"Based on the following reflection on the previous solution:\n{reflection}\n\nRevise your approach accordingly to produce a more robust and accurate final answer."
        )

        return final_answer