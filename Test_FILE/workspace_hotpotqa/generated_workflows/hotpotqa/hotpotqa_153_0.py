# Workflow ID: hotpotqa_153_0
# Benchmark: hotpotqa
# Data Indices: [3986, 2536, 2837, 84, 3052]

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
        then refines the solution through review and ensembles multiple attempts.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps: identify key entities, find connections between them, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an independent direct answer for comparison
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the two solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[multi_hop_solution, direct_answer])

        # Step 4: Review the ensemble result for refinement
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer