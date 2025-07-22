# Workflow ID: hotpotqa_135_0
# Benchmark: hotpotqa
# Data Indices: [3614, 115, 2833, 2897]

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
        It generates multiple reasoning paths using different Custom instructions,
        then ensembles the best solution, and finally reviews it for accuracy.
        """
        # Step 1: Generate multiple solutions using different reasoning prompts
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities first, then tracing connections between them.")
        solution3 = await self.custom(instruction="Think step by step: what do we know? What do we need to find? How can we connect the dots?")
        
        # Step 2: Ensemble the solutions to select the best one
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Review the ensembled solution to improve accuracy
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer