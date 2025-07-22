# Workflow ID: hotpotqa_370_0
# Benchmark: hotpotqa
# Data Indices: [484, 834, 1745, 677, 919]

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
        # into smaller steps and trace connections across information sources.
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace how each piece of information connects to the next.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_facts", "find_connections", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the solution based on the structured reasoning.
        synthesized_solution = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise answer with logical explanation."
        )

        # Step 3: Use Review to validate and refine the synthesized solution.
        final_solution = await self.review(pre_solution=synthesized_solution)

        return final_solution