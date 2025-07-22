# Workflow ID: hotpotqa_407_0
# Benchmark: hotpotqa
# Data Indices: [1982, 3164, 3311, 3187]

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
        Uses FlexibleCustom with sequential reasoning steps to break down complex problems.
        """
        # Step 1: Use flexible custom to extract entities and key information from the problem
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem by identifying all key entities and relevant facts.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an answer based on structured reasoning path
        solution2 = await self.answer_generate()

        # Step 3: Review the generated answer using the structured solution
        reviewed_solution = await self.review(pre_solution=solution2)

        # Step 4: Ensemble multiple solutions (structured + reviewed) for robustness
        final_solution = await self.sc_ensemble(solutions=[solution1, reviewed_solution])

        return final_solution