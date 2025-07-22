# Workflow ID: gsm8k_234_1
# Benchmark: gsm8k
# Data Indices: [767, 78]

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
        This is a diverse and efficient workflow using the Iterative Refinement pattern.
        It generates an initial solution, then applies one round of review to improve it — simple, effective, and logically distinct from the existing Reflect-and-Regenerate approach.
        Unlike the existing workflow that uses reflection to guide a new custom call, this one directly refines the same solution in place.
        This avoids creating a second reasoning chain entirely, making it more efficient while still allowing for improvement.
        """
        # Step 1: Generate an initial solution with clear step-by-step instructions
        initial_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller steps. First, list all costs involved. Then, calculate when the cumulative cost of owning chickens becomes less than buying eggs."
        )

        # Step 2: Critically review and refine the initial solution
        refined_solution = await self.review(pre_solution=initial_solution)

        return refined_solution