# Workflow ID: hotpotqa_800_0
# Benchmark: hotpotqa
# Data Indices: [3383, 3080, 3780, 2283, 929]

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
        It uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key steps
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps by identifying key entities and connections.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly using AnswerGenerate for baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble multiple solutions (including direct answer and refined one)
        solutions = [solution1, solution2, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer