# Workflow ID: hotpotqa_320_0
# Benchmark: hotpotqa
# Data Indices: [2635, 2994, 2021, 3852, 792]

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
        It uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key steps (extract, connect, synthesize)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear reasoning steps: extract entities, find connections, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an independent answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[multi_hop_solution, direct_answer])

        # Step 4: Review the ensemble result for refinement
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer