# Workflow ID: gsm8k_222_1
# Benchmark: gsm8k
# Data Indices: [171, 580, 170]

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
        1. Generate 3 independent solutions via parallel ensemble (fan-out).
        2. Select the best solution using ScEnsemble.
        3. Critically reflect on that solution to uncover hidden flaws or assumptions.
        4. Use the reflection to guide a targeted regenerative step with FlexibleCustom in iterative mode.
        
        This combines:
        - Parallel Ensemble for robustness (multiple starting points)
        - Reflect to surface meta-level issues not caught by simple review
        - Iterative refinement guided by reflection (not blind iteration)
        
        Logic is fundamentally different from existing: it uses feedback from reflection to shape the next generation—not just repeated editing.
        """
        # Step 1: Generate multiple diverse initial solutions using flexible custom in parallel
        solutions = []
        for _ in range(3):
            sol = await self.flexible_custom(
                reasoning_pattern="sequential",
                steps=["identify", "formulate", "solve", "check"],
                custom_instruction="Approach this problem as if you're teaching someone new—be explicit about each step."
            )
            solutions.append(sol)

        # Step 2: Pick the strongest candidate using ensemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution—don’t fix yet, just analyze
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate using a tailored instruction based on reflection
        final_solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "rethink_assumptions", "reconstruct"],
            max_iterations=2,
            custom_instruction=f"Based on the following reflection, rework the solution:\n{reflection}"
        )

        return final_solution