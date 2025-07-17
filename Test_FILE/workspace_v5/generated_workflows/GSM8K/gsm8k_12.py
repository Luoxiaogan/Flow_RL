# Benchmark: GSM8K
# Workflow ID: gsm8k_12
# Data Indices: [150, 151, 152]
# Generation Time: 2025-07-17 19:31:17
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
        solution_1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solution_2 = await self.review(pre_solution=solution_1)
        solution_3 = await self.custom(instruction="Can you evaluate the previous solution and provide an improved version?")
        final_solution = await self.sc_ensemble(solutions=[solution_1, solution_2, solution_3])

        return final_solution