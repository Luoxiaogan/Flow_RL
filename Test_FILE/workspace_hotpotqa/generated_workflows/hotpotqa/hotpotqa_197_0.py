# Workflow ID: hotpotqa_197_0
# Benchmark: hotpotqa
# Data Indices: [1110, 19, 1834, 3163, 2221]

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
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions using different custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")
        solution2 = await self.custom(instruction="Solve by identifying key entities and connecting them through logical inference.")
        solution3 = await self.custom(instruction="Think step by step: first identify what information is needed, then find it in context, and finally synthesize the answer.")

        # Step 2: Ensemble the solutions to get a more robust answer
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution for consistency and correctness
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer