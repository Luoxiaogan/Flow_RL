# Workflow ID: hotpotqa_860_0
# Benchmark: hotpotqa
# Data Indices: [2327, 670, 2225, 1916]

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
        It uses FlexibleCustom with sequential reasoning to extract and connect facts,
        then synthesizes the answer using Custom, and finally validates it via Review.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # into smaller steps (e.g., identify key entities, find connections, trace reasoning path)
        intermediate_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a clear and structured answer based on intermediate solution
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step breakdown, generate a concise and accurate final answer."
        )

        # Step 3: Use Review to validate the synthesized answer against the original problem
        validated_answer = await self.review(pre_solution=synthesized_answer)

        return validated_answer