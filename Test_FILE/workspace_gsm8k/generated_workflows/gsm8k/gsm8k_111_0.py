# Workflow ID: gsm8k_111_0
# Benchmark: gsm8k
# Data Indices: [641, 94]

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
        Iterative Refinement Workflow: Generate an initial solution, then refine it twice using Review.
        This structure ensures progressive improvement without requiring ensembling or reflection.
        """
        # Step 1: Generate an initial solution using a general-purpose reasoning instruction
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First, identify what is given and what needs to be found. Then, apply relevant mathematical operations logically."
        )

        # Step 2: Apply iterative refinement — review once to catch obvious errors
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second refinement — improve clarity, structure, and accuracy
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution