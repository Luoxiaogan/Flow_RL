# Workflow ID: hotpotqa_450_0
# Benchmark: hotpotqa
# Data Indices: [3509, 842, 1756, 817, 3798]

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
        It uses flexible custom reasoning to break down the problem step-by-step,
        then synthesizes the answer from extracted connections and entities.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities, find connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally review the solution for refinement
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer using direct generation as a fallback or verification
        final_answer = await self.answer_generate()

        # Step 4: Ensemble the two solutions for robustness
        ensemble_result = await self.sc_ensemble(solutions=[reviewed_solution, final_answer])

        return ensemble_result