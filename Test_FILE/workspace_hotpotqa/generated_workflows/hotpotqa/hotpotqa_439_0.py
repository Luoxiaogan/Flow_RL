# Workflow ID: hotpotqa_439_0
# Benchmark: hotpotqa
# Data Indices: [1570, 582, 1118, 1800]

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
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the solution with a custom operator, and finally validates it via review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller, logical steps and trace the connections between them.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a detailed answer based on the reasoning path
        synthesis = await self.custom(
            instruction="Based on the reasoning path, generate a comprehensive and logically structured answer."
        )

        # Step 3: Review the synthesized answer to ensure accuracy and clarity
        final_answer = await self.review(pre_solution=synthesis)

        return final_answer