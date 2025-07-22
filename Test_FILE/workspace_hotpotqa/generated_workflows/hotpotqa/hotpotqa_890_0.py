# Workflow ID: hotpotqa_890_0
# Benchmark: hotpotqa
# Data Indices: [3091, 1390, 1428, 1602]

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
        Uses FlexibleCustom for structured reasoning and ensembling for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on extracting key entities, finding connections between them, and synthesizing the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve reliability
        final_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        return final_solution