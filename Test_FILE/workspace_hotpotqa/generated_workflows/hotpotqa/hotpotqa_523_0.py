# Workflow ID: hotpotqa_523_0
# Benchmark: hotpotqa
# Data Indices: [2864, 2249, 3503, 213]

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
        It uses FlexibleCustom with sequential reasoning steps to break down the problem,
        then refines the solution through review and ensembles multiple solutions if needed.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using extract_entities, find_connections, and synthesize_answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Review the initial solution for correctness and clarity
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an alternative answer directly (for ensemble)
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble the reviewed solution and direct answer
        final_solution = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_solution