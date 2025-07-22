# Workflow ID: hotpotqa_71_0
# Benchmark: hotpotqa
# Data Indices: [2060, 409, 3420, 2139, 3167]

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
        It uses FlexibleCustom for structured multi-hop reasoning, followed by review and ensemble for robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between key entities.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Review the generated solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 3: Generate an alternative answer using direct generation for comparison
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble both solutions to select the best one
        final_solution = await self.sc_ensemble(solutions=[reviewed_solution, direct_answer])

        return final_solution