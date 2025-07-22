# Workflow ID: hotpotqa_124_0
# Benchmark: hotpotqa
# Data Indices: [3148, 75, 3814, 541, 8]

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
        Uses FlexibleCustom for structured reasoning and ensembles solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to break down the problem with structured multi-hop reasoning
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using structured reasoning.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the initial solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the direct answer and the reviewed solution for better accuracy
        solutions = [solution2, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer