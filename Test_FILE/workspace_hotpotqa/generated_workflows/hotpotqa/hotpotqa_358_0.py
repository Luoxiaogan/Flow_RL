# Workflow ID: hotpotqa_358_0
# Benchmark: hotpotqa
# Data Indices: [828, 1553, 2633, 1564]

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
        This is a streamlined workflow for multi-hop question answering using FlexibleCustom
        with structured reasoning steps: extract_entities, find_connections, synthesize_answer.
        """
        # Step 1: Use FlexibleCustom to perform multi-hop reasoning in a sequential manner
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, first identifying key entities, then finding connections between them, and finally synthesizing a clear answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline (for ensemble)
        baseline_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom result with the baseline to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, baseline_answer])

        # Step 4: Review the ensembled solution for clarity and correctness
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer