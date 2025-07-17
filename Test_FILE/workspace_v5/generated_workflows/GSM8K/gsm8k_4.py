# Benchmark: GSM8K
# Workflow ID: gsm8k_4
# Data Indices: [70, 71, 72]
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
        # Step 1: Use Custom to break down the problem into detailed steps
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Review the generated solution for clarity and correctness
        reviewed_solution = await self.review(pre_solution=step_by_step)

        # Step 3 (Optional): If multiple solutions are available, use ScEnsemble to select the best one
        # ensemble_solution = await self.sc_ensemble(solutions=[step_by_step, reviewed_solution])

        # Final Output
        return reviewed_solution