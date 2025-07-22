# Workflow ID: hotpotqa_54_0
# Benchmark: hotpotqa
# Data Indices: [7, 1404, 1048, 740, 143]

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
        This is a robust workflow graph for multi-hop question answering.
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate multiple solutions using different reasoning prompts
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        solution2 = await self.custom(instruction="Solve this by tracing connections between key entities in the context.")
        solution3 = await self.custom(instruction="Think step-by-step to identify intermediate facts needed to answer the question.")

        # Step 2: Ensemble the solutions to find the most consistent answer
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution for accuracy and clarity
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer