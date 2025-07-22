# Workflow ID: hotpotqa_88_0
# Benchmark: hotpotqa
# Data Indices: [3994, 2645, 675, 622]

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
        # Step 1: Generate multiple solutions via Custom with different reasoning prompts
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step in detail.")
        solution2 = await self.custom(instruction="Solve by identifying key facts from context and connecting them logically.")
        solution3 = await self.custom(instruction="Think step by step: first identify what is being asked, then find relevant information, and finally derive the answer.")

        # Step 2: Ensemble the three solutions to get the most robust answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Review the ensembled solution for clarity, logic, and correctness
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer