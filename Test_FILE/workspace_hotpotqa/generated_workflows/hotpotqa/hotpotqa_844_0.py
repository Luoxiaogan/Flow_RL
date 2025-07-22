# Workflow ID: hotpotqa_844_0
# Benchmark: hotpotqa
# Data Indices: [302, 277, 786, 82]

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
            "trace_logical_path",
            "synthesize_final_answer"
        ]
        intermediate_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using sequential reasoning.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesis_instruction = "Based on the step-by-step breakdown, generate a clear and concise answer with full reasoning."
        synthesized_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (even if just one here, this structure allows future expansion)
        solutions = [validated_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer