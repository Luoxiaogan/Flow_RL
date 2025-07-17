# Benchmark: GSM8K
# Workflow ID: gsm8k_7
# Data Indices: [100, 101, 102]
# Generation Time: 2025-07-17 19:31:16
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
        solution1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solution2 = await self.review(pre_solution=solution1)
        solution3 = await self.custom(instruction="Can you evaluate the previous solution and provide an improved version?")
        ensembled_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return ensembled_solution