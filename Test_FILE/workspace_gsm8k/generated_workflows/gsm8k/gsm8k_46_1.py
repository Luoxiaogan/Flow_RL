# Workflow ID: gsm8k_46_1
# Benchmark: gsm8k
# Data Indices: [482, 718]

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
        This is a diverse and robust workflow using a hybrid of Reflect-and-Regenerate + Iterative Refinement.
        1. Start with an initial solution via FlexibleCustom in iterative mode (2 rounds).
        2. Reflect on the final iterative result to uncover potential blind spots.
        3. Use that reflection to guide a new Custom call for a refined solution.
        4. Finally, review the improved answer for clarity and correctness.
        This approach combines meta-cognition (reflection) with structured iteration—unlike the parallel ensemble used previously.
        """

        # --- STEP 1: Generate an initial solution using iterative refinement (FlexibleCustom) ---
        iterative_solution = await self.flexible_custom(
            custom_instruction="Begin with an estimation strategy, then refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["estimate", "refine", "verify"],
            max_iterations=2
        )

        # --- STEP 2: Reflect on the iterative solution to identify weaknesses or assumptions ---
        reflection_text = await self.reflect(pre_solution=iterative_solution)

        # --- STEP 3: Regenerate a new solution based on the reflection ---
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the previous attempt: '{reflection_text}'. "
                        f"Use this insight to generate a more accurate and logically sound solution."
        )

        # --- STEP 4: Final polish — Review for clarity, structure, and correctness ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer