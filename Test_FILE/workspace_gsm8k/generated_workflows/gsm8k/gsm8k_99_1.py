# Workflow ID: gsm8k_99_1
# Benchmark: gsm8k
# Data Indices: [666, 805, 329]

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
        This workflow uses a novel combination of reflection and iterative refinement to improve solution quality.
        Instead of just reviewing blindly, it first reflects on the initial solution to identify potential weaknesses,
        then uses that insight to guide a targeted revision. This meta-cognitive loop ensures deeper improvement than simple review.
        """
        # Step 1: Generate an initial solution using general step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps."
        )

        # Step 2: Critically reflect on the initial solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to generate a refined solution that addresses identified issues
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with improved clarity and correctness."
        )

        # Step 4: Apply another round of review to polish the solution further
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution