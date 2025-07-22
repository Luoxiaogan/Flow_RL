# Workflow ID: hotpotqa_178_0
# Benchmark: hotpotqa
# Data Indices: [3302, 1147, 3788, 2844, 1849]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem,
                                                       reasoning_pattern="sequential",
                                                       steps=["extract_facts", "identify_connections", "trace_reasoning_path", "synthesize_answer"])
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        Uses FlexibleCustom for step-by-step fact extraction and connection tracing,
        then synthesizes with Custom, ensembles multiple solutions if needed,
        and finally reviews the solution for correctness.
        """
        # Step 1: Use FlexibleCustom to break down the problem into smaller steps
        multi_hop_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 2: Generate a synthesized answer based on the structured reasoning
        synthesis = await self.custom(instruction="Based on the extracted facts and connections, generate a clear and concise answer.")

        # Step 3: Ensemble multiple solutions (simulate generating 2-3 versions for robustness)
        solutions = [
            multi_hop_solution,
            synthesis,
            await self.custom(instruction="Generate a direct answer by thinking through the problem step by step.")
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the final solution for clarity, logic, and accuracy
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer