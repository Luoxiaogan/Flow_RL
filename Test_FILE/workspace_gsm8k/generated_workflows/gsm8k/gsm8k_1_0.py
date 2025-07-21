# Workflow ID: gsm8k_1_0
# Benchmark: gsm8k
# Data Indices: [4, 2]

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
        self.reflect = operator.Reflect(self.config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This workflow combines a Parallel Ensemble with Reflect and Regenerate patterns.
        It generates multiple solutions, selects the best one, reflects on it, and then regenerates a refined solution.
        """

        # Step 1: Generate multiple initial solutions using parallel reasoning
        solution_list = []
        for _ in range(3):  # Generate 3 different solutions
            solution = await self.flexible_custom(
                custom_instruction="Break down the problem into logical steps",
                reasoning_pattern="sequential",
                steps=["analyze", "plan", "solve", "verify"]
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to select the best solution from the list
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect on the best solution to identify potential improvements
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new Custom call with improved instructions
        refined_solution = await self.custom(
            instruction=f"Given the following reflection on the solution: '{reflection}'. Now, provide a more accurate and detailed solution."
        )

        return refined_solution