# Workflow ID: hotpotqa_391_0
# Benchmark: hotpotqa
# Data Indices: [2372, 1598, 192, 2934, 2280]

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
        It uses FlexibleCustom for sequential fact extraction and connection,
        Custom for synthesis, and Review for validation to ensure accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the answer based on the structured reasoning
        solution2 = await self.custom(
            instruction="Based on the previous reasoning steps, generate a clear and concise answer that directly addresses the question."
        )

        # Step 3: Ensemble both solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2])

        # Step 4: Review the ensembled solution for potential errors or improvements
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer