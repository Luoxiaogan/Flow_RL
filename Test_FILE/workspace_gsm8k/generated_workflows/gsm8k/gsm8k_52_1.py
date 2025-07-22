# Workflow ID: gsm8k_52_1
# Benchmark: gsm8k
# Data Indices: [217, 15]

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
        Diverse and effective workflow using Iterative Refinement (2+ reviews).
        This structure applies progressive improvement through repeated review cycles,
        mimicking how humans refine their thinking after feedback — not just one pass.
        It avoids ensemble or reflection-based redirection, focusing purely on iterative quality enhancement.
        """
        # Step 1: Generate an initial solution with basic reasoning
        current_solution = await self.custom(
            instruction="Solve the problem step-by-step, explaining each part clearly."
        )

        # Step 2: Apply iterative refinement — review twice to improve clarity, logic, and completeness
        for i in range(2):
            current_solution = await self.review(pre_solution=current_solution)

        return current_solution