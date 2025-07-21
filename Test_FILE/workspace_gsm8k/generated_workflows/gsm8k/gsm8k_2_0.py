# Workflow ID: gsm8k_2_0
# Benchmark: gsm8k
# Data Indices: [3, 0]

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
        This is a complex workflow that combines parallel ensemble with reflective refinement.
        It first generates multiple solutions in parallel, selects the best one, reflects on it,
        and then regenerates a better solution based on the reflection.
        """

        # Step 1: Generate multiple initial solutions using parallel reasoning
        solution_list = []
        for _ in range(3):  # Generate 3 different solutions
            solution = await self.flexible_custom(
                custom_instruction="Break down the problem into logical steps and solve systematically.",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution from the parallel ones
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the best solution to identify potential improvements or flaws
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new, more refined solution
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}. Now, provide a more accurate and detailed solution.",
            reasoning_pattern="iterative",
            steps=["initial_approach", "refine", "finalize"],
            max_iterations=2
        )

        return final_solution