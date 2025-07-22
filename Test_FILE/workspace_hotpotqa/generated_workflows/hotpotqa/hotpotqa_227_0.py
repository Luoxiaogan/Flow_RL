# Workflow ID: hotpotqa_227_0
# Benchmark: hotpotqa
# Data Indices: [297, 601, 3088, 2004]

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
        It uses flexible custom for step-by-step reasoning, then synthesizes with Custom,
        and finally validates the result with Review. Ensemble ensures robustness.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to extract and connect facts
        reasoning_steps = [
            "identify_key_entities",
            "find_intermediate_connections",
            "trace_logical_path",
            "synthesize_final_answer"
        ]
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and trace connections between entities.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the reasoning path
        synthesis_instruction = "Based on the reasoning steps above, write a concise and accurate answer with clear justification."
        synthesized_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Review to validate and refine the answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Ensemble multiple solutions (here we simulate a list with just one solution)
        # In practice, you might generate 2-3 alternative answers using different prompts
        # and ensemble them for higher accuracy
        solution_list = [validated_answer]
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer