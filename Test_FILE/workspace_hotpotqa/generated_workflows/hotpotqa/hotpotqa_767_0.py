# Workflow ID: hotpotqa_767_0
# Benchmark: hotpotqa
# Data Indices: [3601, 2950, 163, 770]

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
            "extract_relevant_facts",
            "find_connections_between_facts",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using sequential reasoning.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to generate an answer based on the structured reasoning
        solution2 = await self.custom(
            instruction="Based on the structured reasoning above, generate a clear and concise answer."
        )

        # Step 3: Ensemble both solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, solution2])

        # Step 4: Review the ensembled solution to validate correctness
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer