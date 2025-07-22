# Workflow ID: gsm8k_11_0
# Benchmark: gsm8k
# Data Indices: [771, 954]

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
        Step 1: Generate 3 independent solutions (Parallel Ensemble).
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on the selected solution to identify potential flaws or improvements.
        Step 4: Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """

        # --- STEP 1: Parallel Ensemble ---
        solution_candidates = []
        for i in range(3):  # Generate 3 different approaches
            candidate = await self.custom(
                instruction="Solve the problem by first identifying all given quantities, then setting up equations or logical steps. Be thorough and avoid assumptions."
            )
            solution_candidates.append(candidate)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Regenerate Based on Reflection ---
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again using an iterative reasoning pattern to ensure accuracy.",
            previous_results=[best_solution],
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        return final_solution