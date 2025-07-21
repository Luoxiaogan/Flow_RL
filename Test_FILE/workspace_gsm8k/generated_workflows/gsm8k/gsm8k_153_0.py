# Workflow ID: gsm8k_153_0
# Benchmark: gsm8k
# Data Indices: [552, 964]

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
        1. Generate 3 independent solutions using FlexibleCustom in 'parallel' mode.
        2. Use ScEnsemble to select the best one.
        3. Reflect on the selected solution to identify potential flaws or improvements.
        4. Regenerate a final solution using Custom with guidance from the reflection.
        This ensures robustness via ensemble, then meta-cognitive refinement.
        """

        # Step 1: Generate multiple candidate solutions in parallel
        parallel_solutions = []
        for _ in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Solve the problem systematically",
                reasoning_pattern="parallel",
                steps=["understand", "decompose", "compute", "verify"]
            )
            parallel_solutions.append(solution)

        # Step 2: Select the best solution using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # Step 3: Reflect on the best solution — no rewriting, just critique
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use reflection to guide a new, improved solution
        final_answer = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be precise and step-by-step."
        )

        return final_answer