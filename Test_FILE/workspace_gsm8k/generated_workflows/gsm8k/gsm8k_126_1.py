# Workflow ID: gsm8k_126_1
# Benchmark: gsm8k
# Data Indices: [745, 354]

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
        This structure combines parallel exploration (multiple strategies) with meta-cognitive refinement.
        Step 1: Generate 3 diverse solutions using different reasoning patterns (parallel).
        Step 2: Use ScEnsemble to select the best one.
        Step 3: Critically reflect on that solution to uncover hidden assumptions or errors.
        Step 4: Regenerate a new solution based on the reflection — this ensures deeper reasoning than simple review.
        
        Why it's different:
        - Uses both parallelism and reflection-based regeneration (not just iterative review).
        - Introduces a conditional logic path where the reflection guides a new generation, not just editing.
        - Avoids linear step-by-step flow; instead, leverages diversity first, then introspection.
        """
        # --- STEP 1: Generate multiple solutions via parallel ensemble ---
        solution_pool = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            solution = await self.flexible_custom(
                custom_instruction="Solve this math problem by focusing on clear, logical steps.",
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_pool.append(solution)

        # --- STEP 2: Select best solution from the pool ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- STEP 3: Reflect critically on the best solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate a new solution informed by reflection ---
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Use this insight to generate a more accurate and robust solution. "
                        f"Ensure all assumptions are explicit and calculations are double-checked."
        )

        return final_answer