# Workflow ID: gsm8k_3_1
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
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This workflow uses a parallel ensemble with iterative refinement.
        It generates multiple solutions, reviews them, and then refines the best one.
        """

        # Step 1: Generate an initial set of solutions using different reasoning patterns
        solution1 = await self.flexible_custom(
            custom_instruction="Break the problem into logical steps and solve systematically.",
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"]
        )

        solution2 = await self.flexible_custom(
            custom_instruction="Approach the problem from multiple angles and compare results.",
            reasoning_pattern="parallel",
            steps=["estimate", "calculate", "cross-check"]
        )

        solution3 = await self.flexible_custom(
            custom_instruction="Start with a rough estimate, then refine step-by-step.",
            reasoning_pattern="iterative",
            steps=["initial_guess", "refine", "finalize"],
            max_iterations=2
        )

        # Step 2: Use ScEnsemble to select the best solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Review the best solution to improve clarity and accuracy
        first_review = await self.review(pre_solution=best_solution)

        # Step 4: Reflect on the reviewed solution to identify potential flaws or improvements
        reflection = await self.reflect(pre_solution=first_review)

        # Step 5: Use the reflection to guide a new, more refined solution
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection: {reflection}. Now, provide a more detailed and accurate solution.",
            reasoning_pattern="iterative",
            steps=["re-evaluate", "refine", "finalize"],
            max_iterations=2
        )

        return final_solution