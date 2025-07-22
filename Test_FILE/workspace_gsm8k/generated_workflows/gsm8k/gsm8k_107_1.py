# Workflow ID: gsm8k_107_1
# Benchmark: gsm8k
# Data Indices: [648, 607, 567]

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
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and effective workflow using the 'Iterative Refinement' pattern.
        It starts with a simple initial solution and applies the Review operator twice
        to progressively improve the answer — mimicking how humans refine their thinking
        through multiple passes of critical evaluation.
        """
        # Step 1: Generate a basic solution using flexible custom in sequential mode
        current_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step.",
            reasoning_pattern="sequential",
            steps=["identify", "compute", "conclude"]
        )

        # Step 2: Apply iterative refinement — review once
        refined_solution_1 = await self.review(pre_solution=current_solution)

        # Step 3: Apply second round of refinement — review again
        refined_solution_2 = await self.review(pre_solution=refined_solution_1)

        return refined_solution_2