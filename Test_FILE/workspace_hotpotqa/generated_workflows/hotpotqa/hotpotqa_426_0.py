# Workflow ID: hotpotqa_426_0
# Benchmark: hotpotqa
# Data Indices: [48, 2357, 3947, 2189, 3417]

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
        Uses FlexibleCustom (sequential) for structured fact extraction and connection,
        then Custom for synthesis, followed by Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and extract relevant facts step-by-step across multiple hops
        reasoning_steps = ["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps, trace connections between entities, and synthesize an answer.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to refine and synthesize the solution based on extracted facts
        synthesized_answer = await self.custom(
            instruction="Based on the previous reasoning, generate a clear and concise answer with justification for each step."
        )

        # Step 3: Use Review to validate and improve the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        return final_answer