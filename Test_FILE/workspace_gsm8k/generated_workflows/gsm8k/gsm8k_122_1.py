# Workflow ID: gsm8k_122_1
# Benchmark: gsm8k
# Data Indices: [62, 712, 485]

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
        Iterative Refinement with Reflective Guidance: 
        Uses a meta-cognitive loop where each refinement is informed by reflection on the previous solution.
        This approach ensures that improvements are not just mechanical but also conceptually grounded.
        """
        # Step 1: Generate an initial solution using a flexible custom operator with iterative reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, focusing on clear logic and explicit assumptions.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=1
        )

        # Step 2: Critically reflect on the initial solution to identify potential flaws or oversights
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted solution attempt
        first_improved = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now solve the problem again, ensuring clarity and correctness."
        )

        # Step 4: First refinement pass — improve structure and precision
        second_refined = await self.review(pre_solution=first_improved)

        # Step 5: Second refinement pass — focus on logical consistency and completeness
        final_solution = await self.review(pre_solution=second_refined)

        return final_solution