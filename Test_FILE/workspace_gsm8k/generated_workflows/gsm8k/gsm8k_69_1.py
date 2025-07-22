# Workflow ID: gsm8k_69_1
# Benchmark: gsm8k
# Data Indices: [528, 799, 240]

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
        Diverse and complex workflow combining Iterative Refinement + Reflect & Regenerate.
        1. Use FlexibleCustom in iterative mode to generate a progressively refined solution.
        2. After each iteration, reflect on the current solution to identify weaknesses or assumptions.
        3. Use that reflection to guide the next iteration — not just refinement, but intentional rethinking.
        4. This mimics how humans solve hard problems: try, fail, reflect, adjust strategy, try again.

        Key differences from existing:
        - No parallel ensemble; instead, sequential iterative improvement with meta-reflection.
        - Uses FlexibleCustom’s built-in iteration logic (max_iterations=3) for structured progression.
        - Reflection is used *during* iteration to inform next step, not just at end.
        - Combines two patterns: Iterative Refinement (for incremental quality gain) + Reflect & Regenerate (for strategic adaptation).
        """

        # Step 1: Initialize flexible custom with iterative reasoning pattern
        iterative_solver = self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_analysis", "plan_strategy", "execute_solution", "verify_and_reflect"],
            max_iterations=3,
            custom_instruction="Begin by analyzing the problem structure and identifying key variables."
        )

        # Step 2: Run iterative process
        final_solution = await iterative_solver()

        # Step 3: Reflect on the final solution — this is where we extract insight about potential blind spots
        reflection = await self.reflect(pre_solution=final_solution)

        # Step 4: If reflection indicates uncertainty or ambiguity, regenerate using new instruction informed by reflection
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower():
            final_answer = await self.custom(
                instruction=f"Based on the following reflection:\n{reflection}\n\nGenerate a revised solution focusing on addressing the identified assumption or uncertainty. Be explicit about your reasoning and avoid vague statements."
            )
        else:
            final_answer = final_solution

        return final_answer