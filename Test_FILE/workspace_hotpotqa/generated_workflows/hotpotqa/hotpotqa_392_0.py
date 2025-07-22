# Workflow ID: hotpotqa_392_0
# Benchmark: hotpotqa
# Data Indices: [436, 2132, 2790, 1286, 3648]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        multi_hop_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=multi_hop_steps
        )

        # Step 2: Use Custom to synthesize the final answer from intermediate reasoning
        synthesized_answer = await self.custom(
            instruction="Based on the reasoning steps above, provide a clear and concise final answer."
        )

        # Step 3: Review the synthesized answer for correctness and clarity
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (e.g., generate a few alternatives for robustness)
        solution_list = [
            synthesized_answer,
            reviewed_answer,
            await self.custom(instruction="Generate an alternative reasoning path and derive the answer again.")
        ]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer