# Workflow ID: hotpotqa_383_0
# Benchmark: hotpotqa
# Data Indices: [1924, 1218, 1210, 32]

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
        Uses FlexibleCustom for structured multi-hop reasoning and ensembles multiple solutions.
        """
        # Step 1: Use FlexibleCustom to perform step-by-step multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, identify key entities, find connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer as a backup
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        # Step 4: Review the ensemble result for refinement
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer