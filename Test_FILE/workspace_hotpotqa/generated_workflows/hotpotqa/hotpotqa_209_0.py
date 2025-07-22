# Workflow ID: hotpotqa_209_0
# Benchmark: hotpotqa
# Data Indices: [2146, 3015, 1627, 425, 2921]

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
        It breaks down the problem step-by-step and traces connections across contexts.
        """
        # Step 1: Use FlexibleCustom to perform sequential multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps, trace connections between pieces of information, and synthesize the final answer.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relations", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Optionally refine with review if needed (e.g., if solution seems incomplete)
        refined_solution = await self.review(pre_solution=solution)

        # Step 3: Ensembling can be skipped here since we have a single strong path from flexible_custom
        # If multiple solutions were generated earlier, ensemble would help. But this is a sequential flow.

        return refined_solution