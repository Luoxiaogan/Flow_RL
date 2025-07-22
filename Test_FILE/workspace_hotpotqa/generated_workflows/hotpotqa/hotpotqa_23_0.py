# Workflow ID: hotpotqa_23_0
# Benchmark: hotpotqa
# Data Indices: [902, 223, 2673, 2340, 3588]

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
        Finally, it reviews the solution for accuracy.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to break down the problem
        reasoning_steps = [
            "identify_key_entities",
            "extract_facts_from_context",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using sequential reasoning to trace connections between entities.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to refine the synthesized answer with clear reasoning
        refined_solution = await self.custom(
            instruction="Explain your reasoning in detail and ensure all steps are logically connected to reach the final answer."
        )

        # Step 3: Ensemble multiple solutions (simulate generating a few via loop if needed)
        solutions = [multi_hop_solution, refined_solution]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the final solution for correctness and clarity
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer