# Workflow ID: gsm8k_108_1
# Benchmark: gsm8k
# Data Indices: [893, 22, 520]

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
        Diverse and effective workflow using the Reflect and Regenerate pattern as the core logic.
        Step 1: Generate an initial solution using Custom with a clear, structured prompt.
        Step 2: Critically reflect on that solution to uncover assumptions, errors, or missing elements.
        Step 3: Use the reflection to guide a new solution via FlexibleCustom in iterative mode — this ensures deep refinement based on meta-cognition.
        This is fundamentally different from the existing workflow because it centers on a single, guided regeneration loop instead of parallel ensembling followed by reflection.
        """

        # --- STEP 1: Initial Solution ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Break it into logical sub-steps and justify each one clearly."
        )

        # --- STEP 2: Reflect on the Solution ---
        reflection_text = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate Using Reflection-Based Iterative Refinement ---
        # Use FlexibleCustom with iterative reasoning pattern to refine the solution based on the reflection
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, improve the solution: {reflection_text}",
            reasoning_pattern="iterative",
            steps=["analyze_reflection", "adjust_assumptions", "recompute_with_corrections"],
            max_iterations=2
        )

        return final_solution