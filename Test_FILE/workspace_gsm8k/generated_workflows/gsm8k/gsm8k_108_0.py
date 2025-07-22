# Workflow ID: gsm8k_108_0
# Benchmark: gsm8k
# Data Indices: [893, 22, 520]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate multiple candidate solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Critically reflect on the selected solution to uncover potential flaws or missed steps.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble ---
        # Generate 3 independent solutions using Custom with different reasoning prompts
        solutions = []
        for i in range(3):
            instruction = f"Approach the problem using a different method (e.g., algebraic, visual, step-by-step). Reason carefully."
            solution = await self.custom(instruction=instruction)
            solutions.append(solution)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection ---
        # Use flexible custom with iterative pattern to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection, improve the solution: " + reflection_text,
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_reasoning", "recompute"],
            max_iterations=2
        )

        return refined_solution