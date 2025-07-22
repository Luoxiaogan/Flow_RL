# Workflow ID: gsm8k_35_1
# Benchmark: gsm8k
# Data Indices: [880, 635]

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
        This is a diverse workflow using the Iterative Refinement pattern.
        It generates an initial solution, then refines it through two rounds of review.
        The logic differs from the existing workflow by focusing on progressive improvement
        rather than parallel exploration or ensemble selection.
        """

        # Step 1: Generate an initial solution with a clear, structured instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations and reasoning. Be precise and thorough."
        )

        # Step 2: First refinement - improve clarity and correctness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement - apply deeper scrutiny to catch subtle errors
        second_refined = await self.review(pre_solution=first_refined)

        # Final output: return the most refined version
        return second_refined