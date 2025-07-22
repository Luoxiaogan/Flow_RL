# Workflow ID: hotpotqa_238_0
# Benchmark: hotpotqa
# Data Indices: [2415, 341, 2915, 3532, 1257]

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
        This is a streamlined workflow graph for multi-hop question answering.
        Uses FlexibleCustom with sequential reasoning to break down the problem step-by-step.
        """
        # Step 1: Use flexible custom to extract key entities and relationships
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem by identifying key entities and their relationships.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an answer based on the structured reasoning
        solution2 = await self.answer_generate()

        # Step 3: Review the generated answer using the structured solution as context
        reviewed_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble the original answer and the reviewed one for final output
        final_solution = await self.sc_ensemble(solutions=[solution2, reviewed_solution])

        return final_solution