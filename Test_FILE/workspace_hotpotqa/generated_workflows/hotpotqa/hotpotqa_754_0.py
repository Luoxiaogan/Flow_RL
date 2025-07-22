# Workflow ID: hotpotqa_754_0
# Benchmark: hotpotqa
# Data Indices: [1200, 2734, 3820, 2040]

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
        It uses flexible custom for sequential reasoning to extract and connect facts,
        then synthesizes the answer using a custom operator, and finally validates with review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down and trace multi-hop connections
        solution_step1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate a refined answer based on the structured reasoning from step 1
        solution_step2 = await self.custom(instruction="Based on the previous reasoning, synthesize a clear and concise final answer.")

        # Step 3: Review the synthesized answer to ensure accuracy and completeness
        final_solution = await self.review(pre_solution=solution_step2)

        return final_solution