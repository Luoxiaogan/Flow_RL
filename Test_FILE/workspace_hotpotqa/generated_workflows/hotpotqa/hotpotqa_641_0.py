# Workflow ID: hotpotqa_641_0
# Benchmark: hotpotqa
# Data Indices: [1102, 3367, 3037, 2855, 450]

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
        It uses FlexibleCustom for structured multi-hop reasoning and ensembles results for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using entity extraction, connection finding, and synthesis.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve accuracy
        final_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        return final_solution