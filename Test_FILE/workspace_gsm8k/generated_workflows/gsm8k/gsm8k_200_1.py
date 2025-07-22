# Workflow ID: gsm8k_200_1
# Benchmark: gsm8k
# Data Indices: [384, 31]

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
        Diverse workflow using Parallel Ensemble + Iterative Refinement (different from existing).
        1. Generate 3 solutions via parallel ensemble with varied reasoning styles.
        2. Select the best one using ScEnsemble.
        3. Apply iterative refinement: use Review to improve it in a loop up to 2 times.
        4. Final review for consistency and clarity.
        
        This logic differs from the original by:
        - Using iterative refinement after ensemble instead of reflection-guided regeneration
        - Applying multiple rounds of improvement (not just one) on the top candidate
        - Not involving Reflect at all — instead relying on structured review cycles
        - Keeping the core "generate → select → refine" structure but changing the refinement strategy
        """
        # Step 1: Parallel Ensemble — Generate 3 diverse solutions
        solution_candidates = []
        strategies = [
            "Break the problem into steps, solve each step independently.",
            "Use algebraic modeling: define variables and equations first.",
            "Think like a real-world person solving this — what would you do first?"
        ]
        for i, strategy in enumerate(strategies):
            candidate = await self.custom(instruction=strategy)
            solution_candidates.append(candidate)

        # Step 2: Select the most consistent solution
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Iterative Refinement — Improve the selected solution up to 2 times
        current_solution = best_solution
        for iteration in range(2):  # Max 2 refinement passes
            improved = await self.review(pre_solution=current_solution)
            # If no improvement is detected, stop early (heuristic)
            if improved == current_solution:
                break
            current_solution = improved

        # Step 4: Final quality check — ensure clarity and correctness
        final_solution = await self.review(pre_solution=current_solution)

        return final_solution