# Workflow ID: gsm8k_171_0
# Benchmark: gsm8k
# Data Indices: [147, 459, 535]

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
        This is a diverse and effective workflow using the Iterative Refinement pattern.
        It starts with a basic solution, then refines it twice using Review to improve accuracy and clarity.
        """
        # Step 1: Generate an initial solution using a general-purpose instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, clearly identifying each calculation needed."
        )

        # Step 2: First refinement - improve clarity and structure
        first_refined = await self.review(
            pre_solution=initial_solution
        )

        # Step 3: Second refinement - enhance correctness and completeness
        second_refined = await self.review(
            pre_solution=first_refined
        )

        # Final output: return the most refined version
        return second_refined