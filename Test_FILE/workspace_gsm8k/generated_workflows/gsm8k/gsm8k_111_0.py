# Workflow ID: gsm8k_111_0
# Benchmark: gsm8k
# Data Indices: [918, 212]

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
        Diverse workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on that solution to identify potential flaws or missed logic.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- STEP 1: Parallel Ensemble ---
        solution_pool = []
        for i in range(3):
            instruction = "Solve the problem by considering multiple possible interpretations of the scenario. Provide clear reasoning for each step."
            solution = await self.custom(instruction=instruction)
            solution_pool.append(solution)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Using Reflection as Guidance ---
        # Use FlexibleCustom in iterative mode to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection, improve the solution by addressing any logical gaps or assumptions: " + reflection,
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_logic", "verify_consistency"],
            max_iterations=2
        )

        return refined_solution