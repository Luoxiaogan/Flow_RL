# Benchmark: GSM8K
# Workflow ID: gsm8k_9
# Data Indices: [120, 121, 122]
# Generation Time: 2025-07-17 19:31:15
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
        step1 = await self.custom(instruction="Can you break down the problem into smaller steps and explain the reasoning behind each step?")
        step2 = await self.review(pre_solution=step1)
        solution = await self.sc_ensemble(solutions=[step1, step2])

        return solution