# Workflow ID: gsm8k_211_1
# Benchmark: gsm8k
# Data Indices: [230, 821, 634]

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
        Diverse and complex workflow using the Reflect-and-Regenerate pattern as the core logic.
        1. Generate an initial solution via Custom.
        2. Critically reflect on it to uncover hidden assumptions or errors (Reflect).
        3. Use that reflection to guide a structured, multi-step reasoning process via FlexibleCustom in iterative mode.
        4. Return the final refined answer — no ensemble, no review, just deep reflection-driven regeneration.

        This is fundamentally different from the existing workflow because:
        - It uses only one initial solution + reflection → regeneration, not parallel ensembling.
        - It leverages FlexibleCustom with iterative reasoning for deeper refinement.
        - It avoids ScEnsemble entirely, relying instead on meta-cognitive insight from reflection.
        - The flow is strictly sequential but deeply introspective, focusing on quality of thought over quantity of attempts.
        """
        # Step 1: Generate an initial solution
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, showing all calculations clearly.")

        # Step 2: Reflect critically on the solution — identify potential flaws, oversights, or assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, structured, iterative solution process
        # This is the key difference: we don't just fix the old solution — we rebuild it with better reasoning
        final_answer = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection, solve the problem again with improved clarity and accuracy: {reflection}",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        return final_answer