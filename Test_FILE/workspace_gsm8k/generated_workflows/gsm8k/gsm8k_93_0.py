# Workflow ID: gsm8k_93_0
# Benchmark: gsm8k
# Data Indices: [118, 653, 710]

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
        Step 1: Generate multiple independent solutions (Parallel Ensemble).
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect critically on the selected solution to uncover potential flaws or improvements.
        Step 4: Use reflection to guide a new, improved solution via FlexibleCustom with iterative refinement.
        """
        # --- PARALLEL ENSEMBLE: Generate 3 diverse initial solutions ---
        solution_list = []
        for i in range(3):
            instruction = "Solve this math problem by considering different approaches: algebraic, step-by-step arithmetic, and logical reasoning. Provide clear explanations."
            solution = await self.custom(instruction=instruction)
            solution_list.append(solution)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # --- REFLECT: Critically analyze the best solution without rewriting it ---
        reflection_text = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE USING REFLECTION: Use reflection to guide a more robust solution ---
        # Now we use FlexibleCustom with an iterative pattern to refine based on reflection
        refined_solution = await self.flexible_custom(
            custom_instruction="Based on the following reflection: " + reflection_text +
                               " Apply an iterative approach to improve accuracy and address potential blind spots.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "identify_assumptions", "refine_logic", "verify_final_answer"],
            max_iterations=2
        )

        return refined_solution