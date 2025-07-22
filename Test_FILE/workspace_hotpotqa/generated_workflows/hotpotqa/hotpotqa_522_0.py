# Workflow ID: hotpotqa_522_0
# Benchmark: hotpotqa
# Data Indices: [1400, 1282, 1273, 3039, 1311]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem step by step.
        """
        # Step 1: Use FlexibleCustom to extract entities and key information from the problem
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and identify key entities and relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer using the structured reasoning output
        solution2 = await self.answer_generate()

        # Step 3: Review the generated answer to improve accuracy
        reviewed_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble the original and reviewed solutions to select the best one
        final_solution = await self.sc_ensemble(solutions=[solution1, reviewed_solution])

        return final_solution