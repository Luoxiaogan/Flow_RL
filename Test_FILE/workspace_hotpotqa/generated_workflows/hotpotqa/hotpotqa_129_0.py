# Workflow ID: hotpotqa_129_0
# Benchmark: hotpotqa
# Data Indices: [234, 3462, 252, 999, 1004]

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
        # Step 1: Generate multiple reasoning paths via Custom with different prompts
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        solution2 = await self.custom(instruction="Solve this by tracing connections between key pieces of information in the context.")
        solution3 = await self.custom(instruction="First identify all entities mentioned, then find relationships between them to derive the answer.")

        # Step 2: Ensemble the solutions to select the most consistent one
        solutions = [solution1, solution2, solution3]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Final review to refine or validate the ensembled solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer