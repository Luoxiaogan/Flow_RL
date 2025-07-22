# Workflow ID: hotpotqa_96_0
# Benchmark: hotpotqa
# Data Indices: [1724, 3530, 1292, 3196, 1335]

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
        then Custom for synthesis, followed by Review for validation, and finally
        ScEnsemble to select the best solution from multiple attempts.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across context pieces
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear answer based on the structured reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a concise and accurate final answer."
        )

        # Step 3: Use Review to refine the synthesized answer by checking for logical consistency
        refined_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Generate multiple solutions via iterative refinement (simulated with a loop)
        solutions = []
        for _ in range(3):  # Generate 3 variations using different prompts
            alt_solution = await self.custom(
                instruction="Re-solve this problem by focusing on the most critical connections between entities and facts."
            )
            solutions.append(alt_solution)

        # Step 5: Ensemble the best solution from the list of alternatives
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer