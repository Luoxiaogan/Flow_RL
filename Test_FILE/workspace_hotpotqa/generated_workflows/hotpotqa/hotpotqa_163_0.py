# Workflow ID: hotpotqa_163_0
# Benchmark: hotpotqa
# Data Indices: [3692, 1670, 3894, 1208]

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
        solution_1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each step in detail.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the solution based on the structured breakdown
        solution_2 = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Review the synthesized answer to ensure correctness and clarity
        final_solution = await self.review(pre_solution=solution_2)

        return final_solution