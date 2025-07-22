# Workflow ID: gsm8k_59_1
# Benchmark: gsm8k
# Data Indices: [615, 522, 142]

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
        This workflow combines two fundamentally different patterns:
        1. **Parallel Ensemble (Fan-out/Fan-in)**: Generate 3 distinct solutions using different reasoning strategies.
        2. **Reflect and Regenerate**: Take the best solution from the ensemble, reflect on it critically, then regenerate a refined version based on that reflection — creating a meta-cognitive loop.

        Unlike the existing workflow (which uses Reflect + Custom in a linear sequence), this one:
        - Uses parallel exploration to avoid over-reliance on a single initial approach
        - Applies reflective critique *after* selection, not before
        - Leverages both ScEnsemble and FlexibleCustom for diverse control flow

        Total steps: 6 (within recommended range of 3–8)
        """

        # Step 1: Generate 3 independent solutions using different reasoning strategies
        # Each uses a unique instruction to encourage divergent thinking
        solutions = [
            await self.custom(instruction="Solve using direct arithmetic: identify known values, apply operations step-by-step."),
            await self.custom(instruction="Break the problem into smaller sub-problems. Solve each one individually, then combine results."),
            await self.custom(instruction="Assume an answer and work backwards to verify if it fits all conditions.")
        ]

        # Step 2: Use ScEnsemble to pick the best solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the selected solution to uncover hidden assumptions or gaps
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, improved solution via flexible custom
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}, refine the previous solution to address any overlooked issues.",
            reasoning_pattern="sequential",
            steps=["analyze_reflection", "adjust_assumptions", "recompute", "verify"]
        )

        return final_solution