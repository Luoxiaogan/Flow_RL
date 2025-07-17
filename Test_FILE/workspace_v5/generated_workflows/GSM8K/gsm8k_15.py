# Benchmark: GSM8K
# Workflow ID: gsm8k_15
# Data Indices: [180, 181, 182]
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
        # Step 1: Generate an initial solution by breaking the problem into steps
        initial_solution = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Review the initial solution to refine or improve it
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Optionally ensemble multiple solutions if available (for multi-step problems)
        ensembled_solution = await self.sc_ensemble(solutions=[refined_solution])

        return ensembled_solution