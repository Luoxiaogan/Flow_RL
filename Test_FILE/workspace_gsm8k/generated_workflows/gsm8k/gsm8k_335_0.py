# Workflow ID: gsm8k_335_0
# Benchmark: gsm8k
# Data Indices: [952, 523]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Reflect critically on the selected solution to uncover blind spots or assumptions.
        4. Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- Step 1: Parallel Ensemble ---
        # Generate multiple independent approaches
        solutions = []
        for i in range(3):
            sol = await self.custom(instruction="Solve the problem step-by-step using a different method each time (e.g., algebraic, visual, numerical). Be explicit about your reasoning.")
            solutions.append(sol)

        # --- Step 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- Step 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- Step 4: Regenerate Based on Reflection ---
        # Use flexible custom with iterative pattern to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Improve the following solution based on this reflection: {reflection}. Focus on addressing potential weaknesses identified.",
            reasoning_pattern="iterative",
            steps=["analyze", "refine", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return refined_solution