# Benchmark: GSM8K
# Workflow ID: gsm8k_14
# Data Indices: [170, 171, 172]
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
        # Step 1: Use Custom to break down the problem into detailed steps and explain reasoning
        step_by_step_explanation = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Use Review to refine the solution based on the initial explanation
        refined_solution = await self.review(pre_solution=step_by_step_explanation)

        # Step 3 (Optional): Use ScEnsemble to evaluate multiple solutions if available
        # For now, we assume only one solution is generated
        final_solution = refined_solution

        return final_solution