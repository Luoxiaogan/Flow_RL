# Workflow ID: hotpotqa_469_0
# Benchmark: hotpotqa
# Data Indices: [219, 1884, 1493, 1133]

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
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes an answer with iterative refinement.
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and identify how they are connected.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an initial answer based on structured reasoning
        solution2 = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2])

        # Step 4: Review the ensemble solution for clarity and correctness
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution