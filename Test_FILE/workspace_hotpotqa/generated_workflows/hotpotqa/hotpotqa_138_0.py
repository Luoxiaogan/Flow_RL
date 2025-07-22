# Workflow ID: hotpotqa_138_0
# Benchmark: hotpotqa
# Data Indices: [3639, 2413, 1367, 840]

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
        """
        # Step 1: Use FlexibleCustom to extract entities and find connections in a structured way
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an answer based on initial reasoning
        solution2 = await self.answer_generate()

        # Step 3: Review the generated answer to refine it
        refined_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble the two solutions (original and refined) to get a more robust answer
        final_answer = await self.sc_ensemble(solutions=[solution1, refined_solution])

        return final_answer