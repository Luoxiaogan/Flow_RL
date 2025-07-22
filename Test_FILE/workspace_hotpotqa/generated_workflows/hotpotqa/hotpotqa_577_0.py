# Workflow ID: hotpotqa_577_0
# Benchmark: hotpotqa
# Data Indices: [2579, 858, 261, 1166]

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
        It uses FlexibleCustom for structured multi-hop reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to perform structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities, find connections between them, and synthesize an answer step by step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        return ensemble_solution