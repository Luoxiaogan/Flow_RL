# Workflow ID: hotpotqa_212_0
# Benchmark: hotpotqa
# Data Indices: [1337, 604, 762, 3951]

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
        This is a streamlined workflow for multi-hop question answering using FlexibleCustom for structured reasoning.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and their relationships step-by-step.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate final answer based on structured reasoning
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with original structured solution for robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, reviewed_answer])

        return ensemble_solution