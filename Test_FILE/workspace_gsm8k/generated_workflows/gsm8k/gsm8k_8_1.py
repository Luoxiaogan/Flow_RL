# Workflow ID: gsm8k_8_1
# Benchmark: gsm8k
# Data Indices: [960, 625]

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
        This is a novel workflow using the Reflect-and-Regenerate pattern with iterative refinement via FlexibleCustom.
        Step 1: Use FlexibleCustom in 'iterative' mode to generate an initial solution with structured reasoning.
        Step 2: Critically reflect on that solution to uncover hidden assumptions or logical gaps.
        Step 3: Use the reflection to guide a new, more precise Custom call — not just revising but rethinking from scratch.
        This approach emphasizes meta-cognition and avoids redundancy by leveraging iterative structure for deeper insight.
        """

        # --- STEP 1: Generate Initial Solution Using Iterative Reasoning Pattern ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math word problem step-by-step using systematic logic.",
            reasoning_pattern="iterative",
            steps=["identify_knowns", "define_unknowns", "formulate_equation", "solve", "verify"],
            max_iterations=2
        )

        # --- STEP 2: Reflect on the Initial Solution (Critical Meta-Cognition) ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate Final Answer Based on Reflection ---
        final_instruction = (
            "You have generated an initial solution. Now, critically reflect on it:\n\n"
            f"{reflection}\n\n"
            "Based on these insights, rewrite your solution entirely. Focus on addressing any missing assumptions, unclear steps, or potential errors. "
            "Ensure the final answer is logically rigorous, clearly explained, and free of ambiguity."
        )
        final_answer = await self.custom(instruction=final_instruction)

        return final_answer