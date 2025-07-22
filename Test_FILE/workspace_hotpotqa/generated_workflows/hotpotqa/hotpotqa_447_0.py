# Workflow ID: hotpotqa_447_0
# Benchmark: hotpotqa
# Data Indices: [2680, 1471, 3855, 3747]

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
        # Step 1: Generate multiple solutions via Custom with different step-by-step prompts
        solution1 = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")
        solution2 = await self.custom(instruction="Solve this by identifying key entities and tracing connections between them step by step.")
        solution3 = await self.custom(instruction="First identify all relevant facts in the context, then reason through how they connect to answer the question.")

        # Step 2: Ensemble the three solutions to find the most consistent and well-supported answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        # Step 3: Review the ensembled solution to improve clarity and correctness
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer