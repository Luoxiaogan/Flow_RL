# Workflow ID: hotpotqa_338_0
# Benchmark: hotpotqa
# Data Indices: [1103, 877, 798, 2061]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "extract_relevant_facts", "trace_information_connections", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on structured reasoning
        synthesized = await self.custom(instruction="Based on the detailed reasoning above, generate a clear and concise final answer.")

        # Step 3: Review the synthesized answer for accuracy and clarity
        reviewed = await self.review(pre_solution=synthesized)

        # Step 4: Ensemble with original answer generation for robustness (if needed)
        original = await self.answer_generate()
        ensemble = await self.sc_ensemble(solutions=[reviewed, original])

        return ensemble