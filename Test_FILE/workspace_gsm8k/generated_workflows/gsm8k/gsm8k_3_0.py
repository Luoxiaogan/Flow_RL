# Workflow ID: gsm8k_3_0
# Benchmark: gsm8k
# Data Indices: [5, 7]

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
        self.reflect = operator.Reflect(self.config, self.problem) # New operator
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem) # Flexible custom operator

    async def run_workflow(self):
        """
        This is a workflow graph using the Iterative Refinement pattern.
        """
        # Step 1: Generate an initial solution with general reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Break the problem into logical steps and solve systematically.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        # Step 2: Review the initial solution to improve clarity and accuracy
        first_review = await self.review(pre_solution=initial_solution)

        # Step 3: Reflect on the reviewed solution to identify potential gaps or assumptions
        reflection = await self.reflect(pre_solution=first_review)

        # Step 4: Use the reflection to guide a new, more refined solution
        second_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}. Now, provide a more detailed and accurate solution.",
            reasoning_pattern="iterative",
            steps=["re-evaluate", "refine", "finalize"],
            max_iterations=2
        )

        # Step 5: Final review to ensure the solution is complete and correct
        final_solution = await self.review(pre_solution=second_solution)

        return final_solution