# Workflow ID: hotpotqa_254_0
# Benchmark: hotpotqa
# Data Indices: [29, 1119, 104, 3461]

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
        It uses FlexibleCustom (sequential reasoning) to extract and connect facts,
        then Custom to synthesize the answer, and finally Review to validate it.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information in the context
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace logical connections between facts.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "connect_information", "synthesize_answer"]
        )

        # Step 2: Use Custom to generate a detailed synthesis based on the structured reasoning
        synthesis = await self.custom(
            instruction="Based on the step-by-step reasoning above, provide a clear and concise explanation leading to the final answer."
        )

        # Step 3: Use Review to validate the synthesized solution
        validated_solution = await self.review(pre_solution=synthesis)

        # Optional: Ensemble with direct answer generation for robustness
        direct_answer = await self.answer_generate()
        solutions = [validated_solution, direct_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer