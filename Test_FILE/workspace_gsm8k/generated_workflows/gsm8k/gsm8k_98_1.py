# Workflow ID: gsm8k_98_1
# Benchmark: gsm8k
# Data Indices: [425, 150, 742]

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
        Diverse and robust workflow using Parallel Ensemble with a twist: 
        - Generate 3 solutions using different reasoning styles (step-by-step, formula-first, intuitive).
        - Use ScEnsemble to pick the most consistent one.
        - Apply a final review for polish and clarity — not refinement based on reflection.
        - This avoids iterative loops or meta-reflection, focusing instead on diverse initial approaches and consensus-based selection.
        
        Key differences from existing:
        1. No Reflect-and-Regenerate loop — uses only one round of ensemble + final review.
        2. Uses varied custom instructions per candidate (different reasoning styles) rather than identical prompts.
        3. Does not use FlexibleCustom in an iterative pattern — uses it once for final polishing only.
        """

        # --- PARALLEL ENSEMBLE WITH VARIED STRATEGIES ---
        solution_candidates = []
        strategies = [
            "Solve step-by-step, showing all intermediate calculations clearly.",
            "First identify the core mathematical relationships, then solve using formulas.",
            "Approach intuitively — think like a human solving this quickly without formal steps."
        ]
        
        for strategy in strategies:
            candidate = await self.custom(instruction=strategy)
            solution_candidates.append(candidate)

        # --- SELECT BEST SOLUTION VIA CONSISTENCY ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- FINAL REVIEW FOR CLARITY AND POLISH ---
        polished_solution = await self.review(pre_solution=best_solution)

        return polished_solution