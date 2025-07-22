# Workflow ID: hotpotqa_851_0
# Benchmark: hotpotqa
# Data Indices: [58, 2298, 646, 1547, 2751]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        """
        # Step 1: Use FlexibleCustom with sequential pattern to break down the problem step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the flexible custom solution to refine it
        reviewed_solution = await self.review(pre_solution=solution)

        # Step 4: Ensemble the direct answer and reviewed solution for robustness
        solutions = [direct_answer, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer