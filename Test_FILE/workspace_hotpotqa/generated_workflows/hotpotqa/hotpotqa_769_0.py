# Workflow ID: hotpotqa_769_0
# Benchmark: hotpotqa
# Data Indices: [2896, 1735, 127, 2048, 3644]

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
        reasoning_steps = [
            "identify_key_entities",
            "extract_relevant_facts",
            "find_connections_between_entities",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using sequential reasoning.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a final answer based on extracted information
        synthesis_instruction = "Based on the step-by-step breakdown, provide a clear and concise answer to the question."
        final_answer = await self.custom(instruction=synthesis_instruction)

        # Step 3: Review the final answer to ensure correctness and clarity
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Optional: Ensemble multiple solutions if more are generated (e.g., via loop in future extensions)
        # For now, we return the reviewed answer directly

        return reviewed_answer