# Workflow ID: hotpotqa_103_0
# Benchmark: hotpotqa
# Data Indices: [1590, 1688, 1088, 1261]

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
        It uses flexible custom for step-by-step reasoning, custom for synthesis, 
        and review for validation to ensure accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a detailed answer based on the reasoning path
        synthesized_answer = await self.custom(instruction="Based on the step-by-step reasoning above, generate a clear and concise final answer.")

        # Step 3: Use Review to validate and refine the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble (optional but beneficial) - Generate multiple solutions via Custom for robustness
        solution1 = await self.custom(instruction="Solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step.")
        solution2 = await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step.")
        ensemble_input = [solution1, solution2, validated_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        return final_answer