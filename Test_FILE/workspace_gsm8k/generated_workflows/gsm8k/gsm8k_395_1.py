# Workflow ID: gsm8k_395_1
# Benchmark: gsm8k
# Data Indices: [131, 319, 569]

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
        Iterative Refinement Workflow using Review Operator Twice.
        Starts with a simple solution, then refines it twice via the Review operator.
        This mimics how humans improve answers through multiple rounds of reflection and correction.
        """

        # --- Step 1: Generate an initial solution using a basic Custom prompt ---
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear and concise."
        )

        # --- Step 2: First refinement using Review to improve clarity and logic ---
        first_refined = await self.review(pre_solution=initial_solution)

        # --- Step 3: Second refinement — apply Review again for deeper error detection and polishing ---
        final_answer = await self.review(pre_solution=first_refined)

        return final_answer