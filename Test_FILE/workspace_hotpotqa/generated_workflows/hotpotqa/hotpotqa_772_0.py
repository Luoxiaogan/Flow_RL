# Workflow ID: hotpotqa_772_0
# Benchmark: hotpotqa
# Data Indices: [3094, 2289, 783, 1391]

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
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution and reviews it for final verification.
        """
        # Step 1: Generate multiple solutions via different custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Think step-by-step: identify what needs to be found, then what information is required to find it.")

        # Step 2: Ensemble the three solutions to get a robust answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Review the ensemble solution for accuracy and clarity
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer