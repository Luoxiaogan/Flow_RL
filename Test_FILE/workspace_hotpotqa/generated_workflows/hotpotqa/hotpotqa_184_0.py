# Workflow ID: hotpotqa_184_0
# Benchmark: hotpotqa
# Data Indices: [949, 440, 2126, 3203, 3977]

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
        It uses sequential reasoning to extract and connect facts, then synthesizes the answer.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem into steps
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using sequential reasoning.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear and reasoned answer based on the structured reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the detailed reasoning steps, generate a concise and accurate answer."
        )

        # Step 3: Review the synthesized answer to ensure clarity and correctness
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (including the reviewed one) to improve robustness
        solution_list = [initial_solution, synthesized_answer, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer