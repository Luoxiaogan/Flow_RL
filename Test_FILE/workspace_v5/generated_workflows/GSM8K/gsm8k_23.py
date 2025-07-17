# Benchmark: GSM8K
# Workflow ID: gsm8k_23
# Data Indices: [260, 261, 262]
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
        # Step 1: Use Custom to generate an initial solution by breaking down the problem
        initial_solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Use Review to refine the initial solution
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3 (Optional): Use ScEnsemble to evaluate multiple solutions if available
        # For now, we only have one solution, so we return the refined one directly
        final_solution = refined_solution

        return final_solution