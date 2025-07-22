# Workflow ID: hotpotqa_655_0
# Benchmark: hotpotqa
# Data Indices: [1921, 932, 3846, 3673]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom for synthesis, and Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "find_intermediate_connections", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a detailed answer based on extracted facts
        synthesized_answer = await self.custom(
            instruction="Based on the breakdown of the problem, generate a clear and detailed answer with reasoning."
        )

        # Step 3: Use Review to validate and refine the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Optionally, ensemble with direct answer generation for robustness
        direct_answer = await self.answer_generate()
        solution_list = [validated_answer, direct_answer]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer