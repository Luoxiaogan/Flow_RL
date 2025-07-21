# Workflow ID: gsm8k_57_1
# Benchmark: gsm8k
# Data Indices: [894, 44, 502]

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
        Iterative Refinement Workflow: Start with a basic solution, then improve it through two rounds of review.
        This pattern emphasizes progressive enhancement over ensemble diversity or parallel exploration.
        """
        # Step 1: Generate an initial solution using a general-purpose custom instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations and reasoning clearly."
        )

        # Step 2: First refinement — review to catch errors, clarify logic
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — another review to polish clarity and correctness
        second_refined = await self.review(pre_solution=first_refined)

        # Step 4: Optional final reflection to identify potential blind spots (not used for rewriting)
        reflection = await self.reflect(pre_solution=second_refined)

        # Step 5: Use the reflection as context for one last custom pass to address any overlooked issues
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the previous solution: '{reflection}'. "
                        f"Provide a final, improved version of the answer that addresses these points."
        )

        return final_answer