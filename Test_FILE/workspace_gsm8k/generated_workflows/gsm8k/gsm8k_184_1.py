# Workflow ID: gsm8k_184_1
# Benchmark: gsm8k
# Data Indices: [968, 609]

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
        1. Generate 3 independent solutions (Parallel Ensemble).
        2. Select the best one using ScEnsemble.
        3. Critically reflect on it to uncover hidden assumptions or errors.
        4. Use that reflection to guide a new solution via FlexibleCustom with structured reasoning.
        
        This combines robustness (parallel solutions) with meta-cognition (reflection-guided regeneration),
        creating a more resilient and adaptive solver than simple iterative refinement.
        """
        # Step 1: Generate multiple candidate solutions in parallel
        solution_candidates = []
        for i in range(3):
            candidate = await self.custom(
                instruction="Solve the problem by breaking it into steps. Be thorough but concise. Avoid assumptions."
            )
            solution_candidates.append(candidate)

        # Step 2: Evaluate candidates and select the strongest one
        best_candidate = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the best candidate — identify potential flaws or missed angles
        reflection = await self.reflect(pre_solution=best_candidate)

        # Step 4: Use the reflection to guide a fresh, improved solution via FlexibleCustom
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again with deeper analysis.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            use_structured_output=True
        )

        return final_solution