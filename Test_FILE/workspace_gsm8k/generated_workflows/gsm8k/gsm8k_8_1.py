# Workflow ID: gsm8k_8_1
# Benchmark: gsm8k
# Data Indices: [75, 277, 900]

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
        This is a diverse and robust workflow using the Iterative Refinement pattern.
        Generates an initial solution, then applies two rounds of Review to progressively improve it.
        This mimics how humans refine their thinking — first draft → critique → refinement → second critique → final polish.
        """
        # Step 1: Generate an initial solution using basic reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not worry about perfection yet."
        )

        # Step 2: First review – identify flaws or missing steps in the initial solution
        first_reviewed = await self.review(pre_solution=initial_solution)

        # Step 3: Second review – apply deeper scrutiny based on the first revision
        final_answer = await self.review(pre_solution=first_reviewed)

        return final_answer