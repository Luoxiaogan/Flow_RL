# Workflow ID: gsm8k_183_1
# Benchmark: gsm8k
# Data Indices: [380, 775]

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
        Diverse workflow using Iterative Refinement with a single Custom call followed by Review.
        This is efficient and logically distinct from the existing workflow:
        - No parallel ensemble
        - No reflection-guided regeneration
        - Uses iterative improvement via Review only
        - Simpler structure: 1 initial solution → 2 reviews → final answer
        """
        # Step 1: Generate an initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each reasoning step clearly."
        )

        # Step 2: Apply iterative refinement using Review twice
        refined_solution = await self.review(pre_solution=initial_solution)
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution