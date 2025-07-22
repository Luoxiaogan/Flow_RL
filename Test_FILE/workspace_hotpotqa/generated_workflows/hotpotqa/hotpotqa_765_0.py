# Workflow ID: hotpotqa_765_0
# Benchmark: hotpotqa
# Data Indices: [719, 3268, 3086, 3331, 324]

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
        It uses FlexibleCustom for structured reasoning and ensembles multiple solutions.
        """
        # Step 1: Use flexible custom to break down the problem into key steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps: extract entities, find connections, and synthesize an answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the multi-hop solution to refine it
        refined_solution = await self.review(pre_solution=multi_hop_solution)

        # Step 4: Ensemble the direct answer and the refined multi-hop solution
        final_answer = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return final_answer