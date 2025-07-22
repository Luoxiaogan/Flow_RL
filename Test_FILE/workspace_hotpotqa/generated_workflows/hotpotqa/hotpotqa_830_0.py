# Workflow ID: hotpotqa_830_0
# Benchmark: hotpotqa
# Data Indices: [1163, 221, 20, 2128]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer,
        and finally validates it through review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into smaller steps and trace connections across multiple hops
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace logical connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the reasoning path
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning path above, generate a concise and well-structured answer that directly addresses the question."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        final_answer = await self.review(pre_solution=synthesized_answer)

        # Optional: Ensemble with an alternative solution from a different reasoning approach
        alt_solution = await self.custom(
            instruction="Solve this by first identifying all relevant entities and then connecting them in a logical sequence."
        )
        ensemble_result = await self.sc_ensemble(solutions=[final_answer, alt_solution])

        return ensemble_result