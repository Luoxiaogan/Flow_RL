# Workflow ID: gsm8k_106_1
# Benchmark: gsm8k
# Data Indices: [776, 985]

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
        This is a diverse and complex workflow combining Iterative Refinement + Branching Logic.
        1. Start with an initial solution using FlexibleCustom in sequential mode.
        2. Use Review to improve it iteratively (up to 3 times).
        3. After each review, use Reflect to assess whether the solution is robust enough to stop or continue refining.
        4. If reflection indicates uncertainty or potential error, branch into a parallel ensemble of 3 new approaches.
        5. Select the best from the ensemble and merge it back into the refinement loop for final polishing.
        """
        # --- Step 1: Initial Solution via Sequential Reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem logically and solve step-by-step.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # --- Step 2: Iterative Refinement Loop (Max 3 iterations) ---
        current_solution = initial_solution
        for iteration in range(3):
            # --- Step 2a: Improve with Review ---
            revised_solution = await self.review(pre_solution=current_solution)

            # --- Step 2b: Reflect on Revised Solution ---
            reflection = await self.reflect(pre_solution=revised_solution)

            # --- Step 2c: Conditional Branching Based on Reflection ---
            if "uncertain" in reflection.lower() or "error" in reflection.lower() or "assumption" in reflection.lower():
                # Branch into Parallel Ensemble for more robustness
                print("Branching into Parallel Ensemble due to reflection...")
                ensemble_candidates = []
                for _ in range(3):
                    candidate = await self.flexible_custom(
                        custom_instruction="Solve this problem using a completely different method than before.",
                        reasoning_pattern="sequential",
                        steps=["identify", "plan", "compute", "validate"]
                    )
                    ensemble_candidates.append(candidate)
                
                # Select best from ensemble
                best_from_ensemble = await self.sc_ensemble(solutions=ensemble_candidates)
                
                # Re-assign as current solution to continue refinement
                current_solution = best_from_ensemble
            else:
                # Continue refining without branching
                current_solution = revised_solution

        return current_solution