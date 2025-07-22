# Workflow ID: hotpotqa_283_0
# Benchmark: hotpotqa
# Data Indices: [1432, 2779, 3809, 3515]

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
        It uses flexible custom reasoning to break down the problem into steps,
        then synthesizes the answer based on extracted connections.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract entities and find connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by first extracting key entities, then finding logical connections between them, and finally synthesizing a coherent answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine using Review if needed (e.g., for complex problems)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using AnswerGenerate as a safety net
        final_answer = await self.answer_generate()

        # Step 4: Ensemble with original solution for robustness
        ensemble_result = await self.sc_ensemble(solutions=[refined_solution, final_answer])

        return ensemble_result