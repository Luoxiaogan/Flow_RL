# Workflow ID: gsm8k_186_1
# Benchmark: gsm8k
# Data Indices: [103, 726]

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
        Diverse Workflow: Parallel Ensemble + Reflect and Regenerate
        This workflow first generates 3 independent solutions using parallel reasoning (via FlexibleCustom in 'parallel' mode),
        then selects the best one via ScEnsemble. It then reflects on that winner to identify potential blind spots,
        and finally regenerates a new solution informed by the reflection — combining ensemble robustness with meta-cognitive refinement.
        """
        # Step 1: Generate multiple candidate solutions in parallel (fan-out)
        parallel_solutions = []
        for _ in range(3):
            solution = await self.flexible_custom(
                reasoning_pattern="parallel",
                steps=["analyze", "formulate", "solve"],
                custom_instruction="Solve this problem by considering different possible interpretations of the given information."
            )
            parallel_solutions.append(solution)

        # Step 2: Select the best solution from the ensemble (fan-in)
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a fresh, improved solution
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the previous solution: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Ensure all assumptions are explicit and logically sound."
        )

        return final_solution