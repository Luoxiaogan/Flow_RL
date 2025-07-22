# Workflow ID: hotpotqa_61_0
# Benchmark: hotpotqa
# Data Indices: [2880, 2079, 393, 2212, 3004]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a streamlined workflow graph for multi-hop question answering.
        Uses FlexibleCustom with sequential reasoning to break down the problem,
        then ensembles multiple solutions if needed, and finally reviews the best solution.
        """
        # Step 1: Use FlexibleCustom for structured multi-hop reasoning
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each hop logically.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: If more than one solution is needed (e.g., from multiple reasoning paths), ensemble them
        # For now, we assume one solution suffices — but can be extended
        final_solution = solution

        # Optional: Review to refine the answer
        final_solution = await self.review(pre_solution=final_solution)

        return final_solution