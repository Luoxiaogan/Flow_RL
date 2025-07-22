# Workflow ID: gsm8k_63_1
# Benchmark: gsm8k
# Data Indices: [385, 81]

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
        Diverse and efficient workflow using Iterative Refinement with Review.
        This pattern applies progressive improvement through multiple rounds of critique and rewriting,
        ensuring logical depth without relying on ensembling or reflection-based regeneration.
        """
        # Step 1: Generate an initial solution using a simple Custom call
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: Apply iterative refinement — review twice to progressively improve the solution
        first_revision = await self.review(pre_solution=initial_solution)
        final_solution = await self.review(pre_solution=first_revision)

        return final_solution