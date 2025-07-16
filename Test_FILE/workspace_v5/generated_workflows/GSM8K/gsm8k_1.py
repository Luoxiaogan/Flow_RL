# Benchmark: GSM8K
# Generated from data indices: [5]

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
        step_by_step_analysis = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        code_solution = await self.programmer(analysis=step_by_step_analysis)

        final_solution = await self.review(pre_solution=code_solution)

        return final_solution