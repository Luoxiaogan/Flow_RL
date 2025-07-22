# Workflow ID: hotpotqa_875_0
# Benchmark: hotpotqa
# Data Indices: [3378, 188, 970, 1306]

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
        # and extract relevant information step-by-step (e.g., identify key entities, find connections).
        reasoning_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace the logical connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the extracted facts.
        synthesis = await self.custom(instruction="Based on the reasoning above, generate a clear and concise answer with explicit justification for each step.")

        # Step 3: Review the synthesized solution to validate its logic and correctness.
        reviewed_solution = await self.review(pre_solution=synthesis)

        # Optional: Ensemble with multiple solutions if needed (here we use just one, but structure allows extension)
        # For now, return the reviewed solution as final output.
        return reviewed_solution