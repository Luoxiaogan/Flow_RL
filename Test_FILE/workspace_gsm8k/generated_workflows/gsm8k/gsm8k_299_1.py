# Workflow ID: gsm8k_299_1
# Benchmark: gsm8k
# Data Indices: [871, 203]

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
        Diverse and complex workflow based on the Reflect-and-Regenerate pattern with iterative refinement using FlexibleCustom.
        Step 1: Generate an initial solution via Custom.
        Step 2: Critically reflect on it to uncover hidden assumptions or missed steps (no rewrite yet).
        Step 3: Use the reflection to guide a FlexibleCustom-based regeneration in iterative mode — this ensures structured, step-by-step improvement.
        This approach emphasizes meta-cognition before action, ensuring deep reasoning rather than surface-level fixes.
        """
        # --- Phase 1: Generate Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be explicit about each logical transition and avoid skipping reasoning steps."
        )

        # --- Phase 2: Reflect on the Solution ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Phase 3: Regenerate Using Reflection + Iterative Refinement ---
        # Use FlexibleCustom with iterative pattern to systematically refine the solution based on the reflection
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, improve the solution by addressing potential flaws or gaps: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze", "refine", "verify"],
            max_iterations=3,
            use_structured_output=True
        )

        return final_solution