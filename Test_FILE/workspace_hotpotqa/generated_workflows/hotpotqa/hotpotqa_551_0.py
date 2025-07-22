# Workflow ID: hotpotqa_551_0
# Benchmark: hotpotqa
# Data Indices: [3604, 1667, 3476, 3801]

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
        It uses FlexibleCustom for sequential reasoning to extract and connect facts,
        then Custom to synthesize the answer, followed by Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections between entities or facts across multiple hops.
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and trace connections between relevant facts.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to generate a clear, structured answer based on the reasoning path.
        synthesis = await self.custom(instruction="Based on the step-by-step reasoning, generate a concise and accurate answer.")

        # Step 3: Use Review to validate the synthesized answer for correctness and completeness.
        validated_answer = await self.review(pre_solution=synthesis)

        # Step 4: Ensemble (optional but helpful) — generate a few alternative solutions using Custom
        # and then select the best one via ScEnsemble to improve robustness.
        alt_solutions = [
            await self.custom(instruction="Generate an answer by focusing on the most critical evidence first."),
            await self.custom(instruction="Explain your reasoning as if teaching someone who knows nothing about this topic.")
        ]
        final_answer = await self.sc_ensemble(solutions=[validated_answer] + alt_solutions)

        return final_answer