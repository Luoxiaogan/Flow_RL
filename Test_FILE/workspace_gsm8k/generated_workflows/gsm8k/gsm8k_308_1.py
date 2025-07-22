# Workflow ID: gsm8k_308_1
# Benchmark: gsm8k
# Data Indices: [955, 111]

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
        This is a diverse and efficient workflow using iterative refinement with two rounds of review.
        It starts with an initial solution, then applies the Review operator twice to progressively improve it — 
        mimicking how humans refine their thinking through repeated self-assessment. No reflection or ensemble used here.
        """
        # Step 1: Generate an initial solution
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining your reasoning clearly."
        )

        # Step 2: First refinement via Review — improves clarity, logic flow, and correctness
        current_solution = await self.review(pre_solution=current_solution)

        # Step 3: Second refinement via Review — catches subtle errors or ambiguities missed in first pass
        final_solution = await self.review(pre_solution=current_solution)

        return final_solution