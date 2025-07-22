# Workflow ID: hotpotqa_327_0
# Benchmark: hotpotqa
# Data Indices: [1172, 300, 3816, 132, 1106]

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
        It generates multiple reasoning paths using different custom instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions via different reasoning strategies
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step in detail.")
        solution2 = await self.custom(instruction="Solve by identifying key entities first, then trace connections between them.")
        solution3 = await self.custom(instruction="Think step-by-step: identify what is asked, find relevant facts, and synthesize an answer.")

        # Step 2: Ensemble the solutions to select the most well-supported one
        ensemble_input = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=ensemble_input)

        # Step 3: Review the ensembled solution to improve final accuracy
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer