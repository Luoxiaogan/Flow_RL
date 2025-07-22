# Workflow ID: hotpotqa_886_0
# Benchmark: hotpotqa
# Data Indices: [2792, 2395, 2390, 3411]

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
        # Step 1: Generate multiple solutions using different custom instructions
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities and tracing connections between them.")
        solution3 = await self.custom(instruction="Think step-by-step: first identify what is being asked, then find relevant facts, then combine to derive the answer.")

        # Step 2: Ensemble the three solutions to get the most robust answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Review the ensembled solution for clarity and correctness
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution