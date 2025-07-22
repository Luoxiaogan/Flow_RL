# Workflow ID: hotpotqa_25_0
# Benchmark: hotpotqa
# Data Indices: [3385, 377, 2291, 445]

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
        It generates multiple reasoning paths using different custom instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Generate multiple solutions using different reasoning patterns
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step in detail.")
        solution2 = await self.custom(instruction="Solve by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Think step-by-step: identify what information is needed, find it, and synthesize an answer.")

        # Ensemble the three solutions to select the most coherent and accurate one
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer