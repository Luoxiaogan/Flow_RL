# Workflow ID: hotpotqa_732_0
# Benchmark: hotpotqa
# Data Indices: [332, 3321, 2263, 1362]

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
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using extract_entities, find_connections, and synthesize_answer",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution for refinement
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [solution1, solution2, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer