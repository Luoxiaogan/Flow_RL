# Workflow ID: gsm8k_359_0
# Benchmark: gsm8k
# Data Indices: [278, 147]

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
        Iterative Refinement Workflow for Mathematical Problem Solving.
        This design uses a simple initial solution followed by two rounds of review
        to progressively improve accuracy and clarity — a robust pattern for complex reasoning.
        """
        # Step 1: Generate an initial solution using general-purpose step-by-step reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. First identify known quantities, then apply logical operations to find the unknown. Be explicit in each step."
        )

        # Step 2: Apply iterative refinement — first review
        first_revision = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second review for deeper improvement
        final_solution = await self.review(pre_solution=first_revision)

        return final_solution