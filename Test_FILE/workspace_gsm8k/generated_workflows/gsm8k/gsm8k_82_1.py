# Workflow ID: gsm8k_82_1
# Benchmark: gsm8k
# Data Indices: [271, 492]

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
        This is a diverse and complex workflow combining Iterative Refinement + Reflect-and-Regenerate.
        Step 1: Use FlexibleCustom in iterative mode to generate an initial solution with structured reasoning.
        Step 2: Review the result for clarity and completeness.
        Step 3: Reflect on the reviewed solution to uncover hidden assumptions or gaps.
        Step 4: Use the reflection to guide a new Custom call that synthesizes improved logic.
        Step 5: Final review ensures the answer is polished and logically sound.
        """

        # --- ITERATIVE REFINEMENT WITH FLEXIBLECUSTOM ---
        iterative_solution = await self.flexible_custom(
            custom_instruction="Begin with estimation, then refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["estimate", "analyze", "refine", "verify"],
            max_iterations=2
        )

        # --- REVIEW FOR CLARITY AND COMPLETENESS ---
        refined_solution = await self.review(pre_solution=iterative_solution)

        # --- REFLECT TO UNCOVER ASSUMPTIONS OR GAPS ---
        reflection = await self.reflect(pre_solution=refined_solution)

        # --- USE REFLECTION TO GUIDED REGENERATION ---
        final_answer = await self.custom(
            instruction=f"Given the following solution: {refined_solution}. "
                        f"And here is a critical reflection on it: {reflection}. "
                        f"Based on this reflection, re-solve the problem using clearer structure and deeper analysis."
        )

        # --- FINAL REVIEW TO POLISH THE ANSWER ---
        polished_answer = await self.review(pre_solution=final_answer)

        return polished_answer