# Workflow ID: gsm8k_84_0
# Benchmark: gsm8k
# Data Indices: [420, 196]

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
        This is a diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate multiple solutions via parallel ensemble (robustness).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on it to uncover potential blind spots or assumptions.
        Step 4: Use reflection to guide a new Custom solution for final refinement.
        """
        # --- STEP 1: Parallel Ensemble ---
        # Generate 3 independent solutions using flexible custom with different reasoning patterns
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i % 3]
            solution = await self.flexible_custom(
                custom_instruction="Solve this math word problem by focusing on clarity and accuracy.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1
            )
            solutions.append(solution)

        # --- STEP 2: Ensemble Selection ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflection ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection:\n\n{reflection_text}\n\nNow, provide a revised, improved solution that addresses any weaknesses identified."
        )

        return final_answer