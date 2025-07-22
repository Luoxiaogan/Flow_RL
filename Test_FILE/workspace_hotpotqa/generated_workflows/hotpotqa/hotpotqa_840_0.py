# Workflow ID: hotpotqa_840_0
# Benchmark: hotpotqa
# Data Indices: [2949, 2506, 1142, 3723, 1807]

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
        It uses multiple reasoning paths and ensemble to improve accuracy.
        """
        # Step 1: Generate multiple solutions using different custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities and connecting them logically across the context.")
        solution3 = await self.custom(instruction="Think step by step: first identify what is being asked, then find relevant information, and finally synthesize the answer.")

        # Step 2: Ensemble the three solutions to get a more robust answer
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution for clarity and correctness
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer