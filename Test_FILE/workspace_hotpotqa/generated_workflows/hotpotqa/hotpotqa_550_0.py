# Workflow ID: hotpotqa_550_0
# Benchmark: hotpotqa
# Data Indices: [3830, 3878, 2193, 1392, 2711]

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
        It uses FlexibleCustom for structured reasoning and ensembles multiple solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key steps (extract, connect, synthesize)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, focusing on identifying entities, finding connections between them, and synthesizing a final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve accuracy
        final_answer = await self.sc_ensemble(solutions=[multi_hop_solution, direct_answer])

        return final_answer