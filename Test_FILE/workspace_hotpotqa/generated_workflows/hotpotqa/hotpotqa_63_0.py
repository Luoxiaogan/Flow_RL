# Workflow ID: hotpotqa_63_0
# Benchmark: hotpotqa
# Data Indices: [3562, 806, 2143, 1674, 3224]

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
        Uses FlexibleCustom for structured multi-hop reasoning and ensembles with review for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key steps (extract, connect, synthesize)
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step by extracting relevant entities, finding connections between them, and synthesizing the final answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an alternative direct answer for ensemble
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble both solutions to select the best one
        solution_list = [multi_hop_solution, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 4: Review the final solution for refinement
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution