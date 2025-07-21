# Workflow ID: gsm8k_189_1
# Benchmark: gsm8k
# Data Indices: [141, 728]

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
        Diverse workflow using the Reflect and Regenerate pattern with iterative refinement via FlexibleCustom.
        Step 1: Generate an initial solution using a structured approach (FlexibleCustom with sequential reasoning).
        Step 2: Critically reflect on the solution to uncover assumptions or blind spots.
        Step 3: Use that reflection to guide a new, more robust solution via a second FlexibleCustom call with iterative refinement.
        This mimics human metacognition: solve → analyze → improve.
        """

        # --- INITIAL SOLUTION WITH STRUCTURED REASONING ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this problem by first identifying all given quantities, then defining relationships between them, and finally computing the result.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "define_relationships", "compute_result"]
        )

        # --- CRITICAL REFLECTION STEP ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- ITERATIVE REFINEMENT USING FLEXIBLECUSTOM (Iterative Pattern) ---
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}. Now solve the problem again, focusing on addressing potential flaws in the previous reasoning. Use multiple iterations to refine your answer.",
            reasoning_pattern="iterative",
            steps=["analyze_assumptions", "refine_approach", "verify_consistency"],
            max_iterations=2
        )

        return refined_solution