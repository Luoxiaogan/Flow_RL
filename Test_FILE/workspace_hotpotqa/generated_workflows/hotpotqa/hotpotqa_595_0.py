# Workflow ID: hotpotqa_595_0
# Benchmark: hotpotqa
# Data Indices: [3999, 1607, 490, 2463, 3222]

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
        It uses flexible custom reasoning to break down the problem into steps: extract entities, find connections, and synthesize answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to decompose the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step: first identify key entities, then find connections between them, and finally synthesize the answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Optionally refine the solution using Review if needed
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Generate final answer directly from the refined solution
        final_answer = await self.answer_generate()

        return final_answer