# Workflow ID: gsm8k_340_1
# Benchmark: gsm8k
# Data Indices: [667, 802]

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
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution and applies the `Review` operator twice
        to progressively improve the answer through structured feedback loops.
        This differs from the existing workflow by focusing on iterative refinement
        rather than reflection-guided regeneration, and avoids ensemble or branching logic.
        """
        # Step 1: Generate an initial solution using a basic custom prompt
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear about each calculation."
        )

        # Step 2: Apply first round of review to identify flaws and improve clarity
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Apply second round of review to polish reasoning and fix any remaining issues
        final_solution = await self.review(pre_solution=first_refined)

        return final_solution