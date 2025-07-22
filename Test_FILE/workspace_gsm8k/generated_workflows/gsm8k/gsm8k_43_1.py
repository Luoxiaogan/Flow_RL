# Workflow ID: gsm8k_43_1
# Benchmark: gsm8k
# Data Indices: [760, 505]

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
        This is a diverse and complex workflow using the Reflect and Regenerate pattern as the core logic.
        1. Generate an initial solution (Custom).
        2. Critically reflect on it to uncover hidden assumptions or flaws (Reflect).
        3. Use that reflection to guide a new, improved solution via FlexibleCustom in iterative mode.
        4. If needed, use Review to polish the final output — this ensures clarity and correctness without altering the reasoning path.

        Key differences from existing workflow:
        - No parallel ensemble; instead, uses a single reflective loop for depth over breadth.
        - Uses Reflect + FlexibleCustom (iterative) as the primary improvement engine — not just a fallback.
        - Does NOT use ScEnsemble at all — focuses on one high-quality solution refined through meta-cognition.
        """

        # --- Step 1: Generate initial solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Be explicit about each assumption you make."
        )

        # --- Step 2: Critical reflection on the initial solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Regenerate using the reflection as guidance via iterative refinement ---
        refined_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, improve the solution: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze_assumptions", "correct_errors", "revalidate"],
            max_iterations=2
        )

        # --- Step 4: Final polish using Review to ensure clarity and logical flow ---
        final_answer = await self.review(pre_solution=refined_solution)

        return final_answer