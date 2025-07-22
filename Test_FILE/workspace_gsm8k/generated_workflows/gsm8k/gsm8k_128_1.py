# Workflow ID: gsm8k_128_1
# Benchmark: gsm8k
# Data Indices: [769, 54]

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
        - No parallel ensemble or reflection-guided regeneration
        - Uses only one initial solution + one refinement step
        - Focuses on iterative improvement via review (not reflection + custom)
        - Simpler than the existing logic but still effective
        """
        # Step 1: Generate an initial solution using a clear, step-by-step instruction
        initial_solution = await self.custom(instruction="Solve the problem step-by-step, explaining each reasoning stage clearly.")

        # Step 2: Critically review and refine the solution — this is the core of iterative improvement
        refined_solution = await self.review(pre_solution=initial_solution)

        return refined_solution