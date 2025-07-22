# Workflow ID: gsm8k_168_1
# Benchmark: gsm8k
# Data Indices: [28, 101, 181]

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
        It generates an initial solution, then applies the Review operator twice to progressively improve it.
        This mimics how humans refine their thinking through multiple passes — first catching obvious errors,
        then addressing deeper logical gaps or ambiguities.
        """
        # Step 1: Generate a baseline solution with clear reasoning
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: First refinement pass — improve clarity, fix arithmetic or logic errors
        current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Second refinement pass — address assumptions, edge cases, or alternative interpretations
        final_solution = await self.review(pre_solution=current_solution)

        return final_solution