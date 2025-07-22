# Workflow ID: hotpotqa_155_0
# Benchmark: hotpotqa
# Data Indices: [1214, 3686, 721, 3832]

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
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps: extract key entities, find connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed (e.g., if solution lacks clarity)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Final answer generation (if not already complete in flexible_custom)
        final_answer = await self.answer_generate()

        # Step 4: Ensemble with original and refined solutions for robustness
        ensemble_result = await self.sc_ensemble(solutions=[solution, refined_solution, final_answer])

        return ensemble_result