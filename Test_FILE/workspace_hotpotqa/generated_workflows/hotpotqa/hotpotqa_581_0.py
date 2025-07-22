# Workflow ID: hotpotqa_581_0
# Benchmark: hotpotqa
# Data Indices: [3935, 2834, 879, 2584]

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
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into key entities and trace logical connections step-by-step.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize the final answer based on the structured reasoning
        synthesis_prompt = "Based on the detailed reasoning above, provide a clear and concise final answer."
        final_answer = await self.custom(instruction=synthesis_prompt)

        # Step 3: Review the final answer to validate correctness
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Step 4: Ensemble multiple solutions (if needed) — here we use just one for simplicity
        # In practice, you could generate multiple solutions using different strategies and ensemble them
        solution_list = [multi_hop_solution, final_answer, reviewed_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        return ensembled_solution