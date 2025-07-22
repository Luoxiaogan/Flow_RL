# Workflow ID: gsm8k_287_0
# Benchmark: gsm8k
# Data Indices: [983, 121]

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
        1. Generate 3 independent solutions via parallel ensemble.
        2. Select the best solution using ScEnsemble.
        3. Critically reflect on the selected solution to identify potential flaws or improvements.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- STEP 1: Parallel Ensemble (Fan-out) ---
        solution_list = []
        for i in range(3):  # Generate 3 different approaches
            sol = await self.custom(
                instruction="Solve the problem by breaking it into clear steps. Consider all possible interpretations of the question."
            )
            solution_list.append(sol)

        # --- STEP 2: Select Best Solution ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- STEP 3: Reflect on the Best Solution ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- STEP 4: Conditional Regeneration Based on Reflection ---
        if "error" in reflection.lower() or "assumption" in reflection.lower():
            # If reflection indicates issues, regenerate with guidance
            final_answer = await self.flexible_custom(
                custom_instruction=f"Based on the following reflection: {reflection}. Now solve the problem again with more precision.",
                reasoning_pattern="iterative",
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2
            )
        else:
            # If no major issues found, use a simple Custom to finalize
            final_answer = await self.custom(
                instruction="Refine the current solution based on the following reflection: " + reflection
            )

        return final_answer