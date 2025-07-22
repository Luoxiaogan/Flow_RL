# Workflow ID: hotpotqa_614_0
# Benchmark: hotpotqa
# Data Indices: [1047, 2627, 2992, 3685, 3312]

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
        It uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use flexible custom to extract entities and trace connections in a sequential manner
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and find logical connections between them.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path"]
        )

        # Step 2: Generate an answer directly as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the direct answer using feedback from the structured reasoning
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (structured reasoning + direct answer) for final output
        final_solution = await self.sc_ensemble(solutions=[solution2, reviewed_solution])

        return final_solution