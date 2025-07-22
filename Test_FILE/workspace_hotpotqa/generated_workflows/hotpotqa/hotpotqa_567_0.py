# Workflow ID: hotpotqa_567_0
# Benchmark: hotpotqa
# Data Indices: [2963, 3528, 560, 2122]

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
        It generates multiple reasoning paths using Custom with step-by-step instructions,
        then ensembles the results to select the best answer, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple reasoning paths via Custom with different step-by-step prompts
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Think step by step: identify what information is needed, find it in context, and synthesize the final answer.")

        # Step 2: Ensemble the three solutions to get a more robust answer
        solutions = [solution1, solution2, solution3]
        ensemble_answer = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled answer to refine or verify correctness
        final_answer = await self.review(pre_solution=ensemble_answer)

        return final_answer