# Workflow ID: hotpotqa_756_0
# Benchmark: hotpotqa
# Data Indices: [2020, 1293, 3744, 2493]

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
        It generates multiple reasoning paths using different Custom instructions,
        then ensembles the best solution and reviews it for final verification.
        """
        # Step 1: Generate multiple solutions using different reasoning prompts
        solution1 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solution2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step, focusing on connecting information across different parts of the context.")
        solution3 = await self.custom(instruction="Break down the problem into smaller sub-problems and solve them one by one, ensuring logical connections between each part.")

        # Step 2: Ensemble the solutions to select the most well-supported answer
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution to improve final accuracy
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer