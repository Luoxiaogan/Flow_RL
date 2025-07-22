# Workflow ID: hotpotqa_333_0
# Benchmark: hotpotqa
# Data Indices: [1419, 916, 268, 3]

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
        # into smaller steps and trace connections between pieces of information
        reasoning_steps = [
            "identify_key_entities",
            "extract_facts_from_context",
            "find_intermediate_connections",
            "trace_reasoning_path",
            "synthesize_answer"
        ]
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step using sequential reasoning.",
            reasoning_pattern="sequential",
            steps=reasoning_steps
        )

        # Step 2: Use Custom to synthesize a clear, structured answer based on the multi-hop solution
        final_answer = await self.custom(instruction="Based on the reasoning above, provide a clear and concise answer.")

        # Step 3: Review the synthesized answer for correctness and clarity
        reviewed_answer = await self.review(pre_solution=final_answer)

        # Optional: Ensemble with multiple solutions if needed (e.g., from different reasoning paths)
        # Here we generate one more solution via a simple direct approach for ensemble
        direct_answer = await self.custom(instruction="Solve this problem directly without breaking it down.")
        ensemble_solution = await self.sc_ensemble(solutions=[reviewed_answer, direct_answer])

        return ensemble_solution