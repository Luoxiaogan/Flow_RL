# Workflow ID: hotpotqa_393_0
# Benchmark: hotpotqa
# Data Indices: [914, 2747, 2546, 3617, 3711]

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
        then synthesizes the solution using Custom, and finally validates it via Review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between pieces of information
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_intermediate_connections",
            "synthesize_answer"
        ]
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and explain your reasoning for each step.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Synthesize the final answer from the structured reasoning
        synthesis_instruction = "Based on the detailed reasoning above, generate a clear and concise answer."
        final_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Validate the answer by reviewing it for consistency and correctness
        validated_answer = await self.review(pre_solution=final_answer)

        return validated_answer