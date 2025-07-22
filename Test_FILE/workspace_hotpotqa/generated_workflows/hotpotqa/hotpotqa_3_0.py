# Workflow ID: hotpotqa_3_0
# Benchmark: hotpotqa
# Data Indices: [1188, 1455, 2356, 441, 682]

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
        It uses FlexibleCustom with sequential reasoning to break down the problem,
        then synthesizes the answer effectively.
        """
        # Step 1: Use flexible custom to extract entities and trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and find logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: If needed, refine using review (optional but improves robustness)
        refined_solution = await self.review(pre_solution=solution)

        return refined_solution