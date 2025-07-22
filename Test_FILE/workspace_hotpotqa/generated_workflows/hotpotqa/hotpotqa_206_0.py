# Workflow ID: hotpotqa_206_0
# Benchmark: hotpotqa
# Data Indices: [1281, 2852, 718, 1630, 2729]

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
        # and trace connections between pieces of information
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_intermediate_connections",
            "trace_reasoning_path"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the solution from the multi-hop reasoning
        synthesis_instruction = "Based on the reasoning above, generate a clear and concise answer to the question."
        synthesized_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Review the synthesized answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (if we had more than one) — currently just one
        # In practice, you might run multiple instances of Custom or FlexibleCustom with different prompts
        # and ensemble them. For now, return the reviewed answer directly.
        final_answer = reviewed_answer

        return final_answer