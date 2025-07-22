# Workflow ID: hotpotqa_28_0
# Benchmark: hotpotqa
# Data Indices: [3874, 249, 2466, 536, 751]

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
        then ensembles the best solution using ScEnsemble, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions using different reasoning prompts
        solution1 = await self.custom(instruction="Can you break down the problem into smaller steps and explain each step in detail?")
        solution2 = await self.custom(instruction="Solve this by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Explain how to solve this problem by reasoning step-by-step with clear justification at each stage.")

        # Step 2: Ensemble the solutions to get a robust answer
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution for correctness and clarity
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer