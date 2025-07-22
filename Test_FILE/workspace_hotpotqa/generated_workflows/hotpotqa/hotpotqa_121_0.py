# Workflow ID: hotpotqa_121_0
# Benchmark: hotpotqa
# Data Indices: [1202, 497, 2948, 3912]

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
        then Custom for synthesis, followed by Review for validation.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        # and trace connections across multiple pieces of information
        reasoning_path = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step, identifying key entities and how they relate across different contexts.",
            reasoning_pattern="sequential",
            steps=["identify_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize a coherent answer based on the reasoned path
        synthesized_answer = await self.custom(
            instruction="Based on the step-by-step reasoning above, generate a clear and concise final answer."
        )

        # Step 3: Use Review to validate the synthesized answer
        validated_answer = await self.review(pre_solution=synthesized_answer)

        # Optional: Ensemble with multiple solutions (e.g., from different reasoning paths)
        # Generate a few alternative solutions using Custom for diversity
        solution_list = [
            await self.custom(instruction="Solve this problem by breaking it into detailed steps and explaining each reasoning step."),
            await self.custom(instruction="Explain how to solve the problem with clear reasoning for each step."),
            validated_answer  # Include the reviewed answer as one of the candidates
        ]

        # Step 4: Ensembling to select the best solution
        final_answer = await self.sc_ensemble(solutions=solution_list)

        return final_answer