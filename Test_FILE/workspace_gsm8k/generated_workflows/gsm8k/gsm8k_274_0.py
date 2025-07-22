# Workflow ID: gsm8k_274_0
# Benchmark: gsm8k
# Data Indices: [253, 796, 117]

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
        Diverse and complex workflow combining Parallel Ensemble + Reflect & Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best solution using ScEnsemble.
        Step 3: Reflect on the selected solution to identify potential flaws or improvements.
        Step 4: Use reflection to guide a new Custom call for a refined final answer.
        This structure ensures robustness (from ensemble) and meta-cognition (from reflection).
        """
        # --- PARALLEL ENSEMBLE ---
        solutions = []
        for _ in range(3):  # Generate 3 different approaches
            solution = await self.custom(
                instruction="Solve this math word problem by first identifying what is given, then determining what needs to be found, and finally applying appropriate mathematical operations. Be clear and logical."
            )
            solutions.append(solution)

        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT AND REGENERATE ---
        reflection = await self.reflect(pre_solution=best_solution)

        # Conditional logic based on reflection content — if reflection suggests uncertainty, use iterative refinement
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower():
            final_answer = await self.flexible_custom(
                custom_instruction="Based on the following reflection, improve the solution: " + reflection,
                reasoning_pattern="iterative",
                steps=["analyze_reflection", "adjust_approach", "recompute"],
                max_iterations=2
            )
        else:
            final_answer = await self.custom(
                instruction=f"Given the initial solution and the following reflection: {reflection}. Now, provide a final, improved solution that addresses any identified weaknesses."
            )

        return final_answer