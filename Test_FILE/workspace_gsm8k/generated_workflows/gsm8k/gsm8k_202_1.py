# Workflow ID: gsm8k_202_1
# Benchmark: gsm8k
# Data Indices: [174, 536, 966]

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
        Diverse and efficient workflow using Iterative Refinement (Review-based).
        This structure uses repeated review cycles to progressively improve the solution.
        It avoids reflection or ensemble strategies entirely, focusing solely on iterative feedback loops.
        The logic is fundamentally different from the existing workflow: no reflection, no parallelism, no ensembling — just clean, stepwise refinement via Review.
        """

        # Step 1: Generate an initial solution using a simple but structured approach
        solution = await self.custom(
            instruction="Solve the problem step-by-step. Be clear about each calculation."
        )

        # Step 2: Apply iterative refinement — review twice to improve clarity, accuracy, and completeness
        for i in range(2):
            solution = await self.review(pre_solution=solution)

        return solution