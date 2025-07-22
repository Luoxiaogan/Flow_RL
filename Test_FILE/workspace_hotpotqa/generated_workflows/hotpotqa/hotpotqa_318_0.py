# Workflow ID: hotpotqa_318_0
# Benchmark: hotpotqa
# Data Indices: [2426, 3657, 288, 3983]

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
        This is a robust multi-hop question answering workflow.
        It generates multiple reasoning paths using different instructions,
        then ensembles the best solution, and finally reviews it for correctness.
        """
        # Generate multiple solutions using different step-by-step prompts
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Think step by step: identify what information is needed, find it in context, and combine it logically.")

        # Ensemble the three solutions to select the most well-supported answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Final review to refine and verify the selected solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer