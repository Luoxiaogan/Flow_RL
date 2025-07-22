# Workflow ID: gsm8k_292_0
# Benchmark: gsm8k
# Data Indices: [263, 143]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate multiple independent solutions via parallel ensemble.
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on its weaknesses or assumptions.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble ---
        solution_candidates = []
        for _ in range(3):  # Generate 3 different approaches
            candidate = await self.custom(
                instruction="Solve this math problem by considering a unique strategy. Think step-by-step."
            )
            solution_candidates.append(candidate)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection ---
        # Use FlexibleCustom in iterative mode to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now, solve again with improved clarity and accuracy.",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "reformulate_approach", "execute", "verify"],
            max_iterations=2
        )

        return refined_solution