# Benchmark: GSM8K
# Workflow ID: gsm8k_11
# Data Indices: [140, 141, 142]
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
        # Step 1: Generate an initial solution by breaking down the problem into steps
        initial_solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Review the initial solution to refine and improve it
        reviewed_solution = await self.review(pre_solution=initial_solution)

        # Step 3 (Optional): If multiple solutions exist, ensemble them to select the best one
        # This step is optional and only used if multiple solutions are generated
        # ensembled_solution = await self.sc_ensemble(solutions=[initial_solution, reviewed_solution])

        # Final output: Return the reviewed solution as the final answer
        return reviewed_solution