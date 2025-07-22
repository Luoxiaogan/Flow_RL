# Workflow ID: hotpotqa_663_0
# Benchmark: hotpotqa
# Data Indices: [3389, 2292, 3279, 3567, 1779]

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
        multi_hop_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesis = await self.custom(instruction="Based on the detailed reasoning above, generate a clear and concise final answer.")

        # Step 3: Ensemble multiple solutions (simulate by generating one more solution via Custom)
        solution_list = [
            synthesis,
            await self.custom(instruction="Generate an answer based on the problem context with step-by-step logic.")
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 4: Review the ensembled solution to improve accuracy
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer