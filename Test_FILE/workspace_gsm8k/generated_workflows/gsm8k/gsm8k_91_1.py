# Workflow ID: gsm8k_91_1
# Benchmark: gsm8k
# Data Indices: [773, 854]

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
        1. Generate 3 diverse solutions using parallel reasoning (FlexibleCustom with 'parallel' pattern).
        2. Use ScEnsemble to pick the best one.
        3. Critically reflect on that winner to uncover hidden assumptions or errors.
        4. Regenerate a final solution guided by the reflection — this ensures meta-cognitive improvement beyond simple review.
        
        This design combines:
        - Parallel Ensemble (fan-out/fan-in) for robustness against flawed single-path reasoning
        - Reflect-and-Regenerate for deeper cognitive refinement (not just surface-level editing)
        Unlike the existing workflow, it does not rely on iterative review alone — instead, it uses ensemble selection followed by targeted regeneration based on critical insight.
        """
        # Step 1: Generate multiple independent solutions via parallel reasoning
        parallel_solutions = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Approach the problem from a different angle each time.",
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve", "verify"]
            )
            parallel_solutions.append(solution)

        # Step 2: Select the best solution using ensemble evaluation
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # Step 3: Reflect critically on the selected solution — identify flaws, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution — this is not a simple fix but a rethinking
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Reconstruct the answer from scratch, addressing any identified weaknesses or oversights."
        )

        return final_answer