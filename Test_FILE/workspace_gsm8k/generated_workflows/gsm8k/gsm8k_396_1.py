# Workflow ID: gsm8k_396_1
# Benchmark: gsm8k
# Data Indices: [748, 819]

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
        Iterative Refinement Workflow: Generate an initial solution and refine it twice using the Review operator.
        This pattern focuses on progressive improvement through structured critique, avoiding ensemble or reflection-based loops.
        Unlike the existing workflow, this one uses only a single path of refinement (no branching, no parallelism).
        """
        # Step 1: Generate an initial solution with minimal guidance — let the model start freely
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear and concise."
        )

        # Step 2: First refinement pass — review and improve the initial solution
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass — apply another layer of critical feedback
        second_refined = await self.review(pre_solution=first_refined)

        return second_refined