# Workflow ID: hotpotqa_170_0
# Benchmark: hotpotqa
# Data Indices: [2668, 2684, 2866, 2576]

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
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Generate multiple solutions using different custom instructions to encourage step-by-step reasoning
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities and tracing connections between them.")
        solution3 = await self.custom(instruction="Think step by step: first identify what is being asked, then find relevant information, then synthesize an answer.")

        # Ensemble the three solutions to select the most consistent and well-supported one
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer