# Workflow ID: gsm8k_130_1
# Benchmark: gsm8k
# Data Indices: [511, 722]

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
        Diverse and robust workflow using Parallel Ensemble with early filtering and iterative refinement.
        Step 1: Generate 3 diverse solutions via custom instructions (different reasoning styles).
        Step 2: Use ScEnsemble to select the best one — this acts as a filter before deeper analysis.
        Step 3: Apply Review to improve clarity and correctness of the selected solution.
        Step 4: Finally, use Reflect to identify potential edge cases or assumptions that may have been missed.
        This logic differs from the existing one by emphasizing *early ensemble selection* over post-reflection regen, and by introducing a final reflective check after refinement — not before.
        """
        # --- PARALLEL ENSEMBLE (Fan-out with varied strategies) ---
        solution_candidates = []
        prompts = [
            "Solve step-by-step using arithmetic operations only. Avoid assumptions.",
            "Break the problem into parts: what is given, what needs to be found, and how they connect.",
            "Think like a math teacher: explain each step clearly so a student could follow."
        ]
        for prompt in prompts:
            candidate = await self.custom(instruction=prompt)
            solution_candidates.append(candidate)

        # --- SCENSEMBLE (Fan-in: select top-performing solution based on consistency) ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- REVIEW (Refine the best solution for clarity and accuracy) ---
        refined_solution = await self.review(pre_solution=best_solution)

        # --- FINAL REFLECTION (Meta-cognitive validation — not used for regen but for confidence) ---
        reflection = await self.reflect(pre_solution=refined_solution)

        # Return the refined solution; the reflection can be logged or used externally for debugging
        return refined_solution