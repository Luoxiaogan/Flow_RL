# Workflow ID: hotpotqa_816_0
# Benchmark: hotpotqa
# Data Indices: [430, 3415, 3557, 3241]

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
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple reasoning paths using different custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities and tracing connections between them.")
        solution3 = await self.custom(instruction="Think step-by-step: first identify what is being asked, then gather relevant facts, then synthesize the answer.")

        # Step 2: Ensemble the solutions to select the most well-supported one
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to refine the answer based on its own logic
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer