# Workflow ID: hotpotqa_108_0
# Benchmark: hotpotqa
# Data Indices: [2200, 1350, 1356, 1458, 1809]

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
        # Step 1: Use FlexibleCustom to break down the problem into smaller steps and trace connections
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer based on the structured reasoning from FlexibleCustom
        final_answer = await self.answer_generate()

        # Step 3: Review the generated answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble with original solution (from FlexibleCustom) to reduce errors
        ensemble_result = await self.sc_ensemble(solutions=[solution, reviewed_answer])

        return ensemble_result