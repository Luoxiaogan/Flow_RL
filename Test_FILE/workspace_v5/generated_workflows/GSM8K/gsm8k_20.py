# Benchmark: GSM8K
# Workflow ID: gsm8k_20
# Data Indices: [230, 231, 232]
# Generation Time: 2025-07-17 19:31:14
# Status: generated
# ==================================================

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

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        initial_solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        reviewed_solution = await self.review(pre_solution=initial_solution)

        return reviewed_solution