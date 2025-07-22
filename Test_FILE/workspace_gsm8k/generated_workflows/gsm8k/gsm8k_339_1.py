# Workflow ID: gsm8k_339_1
# Benchmark: gsm8k
# Data Indices: [763, 484, 956]

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
        This workflow uses the Iterative Refinement pattern with a fixed number of refinement steps.
        It starts with an initial solution, then applies Review twice to progressively improve it — 
        mimicking how humans often revise their work multiple times for better accuracy.
        Unlike the existing workflow (which uses Reflect + Custom), this one relies solely on iterative review
        without external reflection or ensemble methods. This creates a fundamentally different logic flow:
        - No branching or parallelism
        - No ensemble selection
        - No meta-cognitive critique via Reflect
        - Only sequential improvement through structured feedback loops
        """

        # Step 1: Generate a clear, step-by-step initial solution
        current_solution = await self.custom(
            instruction="Solve the problem by breaking it down into smaller, manageable steps. Explain each step clearly."
        )

        # Step 2: Apply iterative refinement — refine once, then again
        for i in range(2):  # Exactly two refinement iterations as per the requirement
            current_solution = await self.review(pre_solution=current_solution)

        return current_solution