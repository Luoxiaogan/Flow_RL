# Workflow ID: hotpotqa_277_0
# Benchmark: hotpotqa
# Data Indices: [824, 543, 3172, 3914]

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
        It uses flexible custom reasoning to break down the problem into key steps.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on identifying key entities and their relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        final_answer = await self.answer_generate()

        # Step 3: Ensemble multiple solutions if needed (optional but effective for multi-hop)
        ensemble_solutions = [solution, final_answer]
        ensembled_solution = await self.sc_ensemble(solutions=ensembled_solution)

        # Step 4: Review the final solution for accuracy
        reviewed_solution = await self.review(pre_solution=ensembled_solution)

        return reviewed_solution