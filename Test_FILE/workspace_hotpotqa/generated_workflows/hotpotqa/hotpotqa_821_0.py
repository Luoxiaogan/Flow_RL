# Workflow ID: hotpotqa_821_0
# Benchmark: hotpotqa
# Data Indices: [28, 3269, 1558, 1716]

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
        # and trace connections across multiple pieces of information
        reasoning_steps = [
            "identify_key_entities",
            "extract_facts_from_context",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace how each piece of evidence connects to the final answer.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the solution based on extracted facts
        synthesis_instruction = "Based on the reasoning path above, generate a clear and concise answer with explicit justification for each step."
        synthesized_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Step 4: Optionally ensemble with direct answer generation (as a fallback or cross-check)
        direct_answer = await self.answer_generate()
        ensemble_input = [validated_answer, direct_answer]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        return final_answer