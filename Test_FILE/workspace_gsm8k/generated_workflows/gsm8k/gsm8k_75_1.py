# Workflow ID: gsm8k_75_1
# Benchmark: gsm8k
# Data Indices: [889, 812]

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
        This is a diverse and efficient workflow using the Iterative Refinement pattern with a single initial solution.
        It avoids unnecessary parallelism or reflection loops while still ensuring correctness through structured refinement.
        """
        # Step 1: Generate an initial solution using a well-structured, step-by-step approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by first identifying what is given, then setting up equations or logical steps, and finally computing the answer.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"]
        )

        # Step 2: Apply iterative refinement — review once to improve clarity and correctness
        refined_solution = await self.review(pre_solution=initial_solution)

        return refined_solution