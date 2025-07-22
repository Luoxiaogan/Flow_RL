# Workflow ID: hotpotqa_366_0
# Benchmark: hotpotqa
# Data Indices: [2590, 2865, 3817, 2675]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple hops in the context
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step, identifying key entities and how they connect across different parts of the context.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer from the structured reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble with original reasoning (for robustness) if needed
        ensemble_solutions = [reasoning_solution, validated_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_answer