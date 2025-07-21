# Workflow ID: gsm8k_47_1
# Benchmark: gsm8k
# Data Indices: [52, 628, 905]

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
        This is a diverse workflow using the Iterative Refinement pattern with explicit loops.
        It starts with a simple solution and progressively improves it through two rounds of review.
        Unlike the existing solution, this one avoids reflection-based guidance and instead uses
        repeated refinement via the Review operator — mimicking how humans improve answers by re-examining their work.
        """
        # Step 1: Generate a basic, straightforward solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear but concise. Do not overthink."
        )

        # Step 2: Apply iterative refinement — review twice to polish the answer
        refined_solution = initial_solution
        for i in range(2):  # Two iterations of refinement
            refined_solution = await self.review(pre_solution=refined_solution)

        return refined_solution