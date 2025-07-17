# Benchmark: GSM8K
# Workflow ID: gsm8k_25
# Data Indices: [280, 281, 282]
# Generation Time: 2025-07-17 19:31:18
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
        # Step 1: Generate initial solution by breaking down the problem into steps
        solution_1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Review the initial solution to refine or improve it
        solution_2 = await self.review(pre_solution=solution_1)

        # Step 3: Ensemble multiple solutions (if available) to select the best one
        # For now, we only have one solution, so we can just return it
        final_solution = solution_2

        return final_solution