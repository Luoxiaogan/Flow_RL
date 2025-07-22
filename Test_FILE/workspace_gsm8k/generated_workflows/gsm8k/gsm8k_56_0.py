# Workflow ID: gsm8k_56_0
# Benchmark: gsm8k
# Data Indices: [892, 901]

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
        This is a diverse and iterative refinement workflow using the 'Iterative Refinement' pattern.
        It starts with a basic solution, then refines it twice using the Review operator to improve clarity, correctness, and completeness.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each reasoning step clearly."
        )

        # Step 2: First refinement — improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement — further enhance based on the first iteration
        second_refined = await self.review(pre_solution=first_refined)

        # Step 4: Final output — return the most refined version
        return second_refined