# Benchmark: GSM8K
# Generated from data indices: [10, 11]

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
        self.programmer = operator.Programmer(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph.
        """
        # Step 1: Break down the problem into detailed steps with reasoning
        step_by_step_analysis = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Use the analysis to generate code for solving the problem
        code_solution = await self.programmer(analysis=step_by_step_analysis)

        # Step 3: Review the generated solution for accuracy and clarity
        reviewed_solution = await self.review(pre_solution=code_solution)

        # Step 4: Ensemble multiple solutions (if available) to select the best one
        final_solution = await self.sc_ensemble(solutions=[reviewed_solution])

        return final_solution