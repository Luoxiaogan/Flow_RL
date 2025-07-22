# Workflow ID: hotpotqa_264_0
# Benchmark: hotpotqa
# Data Indices: [778, 3737, 2469, 3678]

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
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem and extract key facts
        reasoning_steps = ["identify_key_entities", "extract_relevant_facts", "trace_information_path", "synthesize_answer"]
        intermediate_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and trace how each piece of information connects to the final answer.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on the extracted facts
        synthesis = await self.custom(instruction="Based on the reasoning above, provide a clear, step-by-step explanation leading to the final answer.")

        # Step 3: Use Review to validate the synthesized solution for consistency and logical flow
        validated_solution = await self.review(pre_solution=synthesis)

        # Step 4: Ensemble multiple solutions (e.g., original + reviewed) for robustness
        ensemble_input = [intermediate_solution, validated_solution]
        final_answer = await self.sc_ensemble(solutions=ensemble_input)

        return final_answer