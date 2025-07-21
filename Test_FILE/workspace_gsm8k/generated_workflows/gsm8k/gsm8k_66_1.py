# Workflow ID: gsm8k_66_1
# Benchmark: gsm8k
# Data Indices: [127, 834]

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
        This is a diverse and robust workflow using the 'Reflect and Regenerate' pattern.
        First, generate an initial solution. Then, critically reflect on it to uncover hidden assumptions or errors.
        Finally, use that reflection to guide a new, improved solution — mimicking human meta-cognition.
        This approach prioritizes deep reasoning over brute-force ensembling.
        """

        # --- STEP 1: Generate an initial solution using general step-by-step reasoning ---
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it into clear steps: identify knowns, unknowns, operations needed, and compute systematically."
        )

        # --- STEP 2: Critically reflect on the initial solution without rewriting it ---
        reflection = await self.reflect(
            pre_solution=initial_solution
        )

        # --- STEP 3: Use the reflection to guide a new, improved solution ---
        final_answer = await self.custom(
            instruction=f"Given the initial solution and the following reflection: '{reflection}'. Now, provide a revised solution that addresses these points while maintaining clarity and correctness."
        )

        return final_answer