# Workflow ID: hotpotqa_299_0
# Benchmark: hotpotqa
# Data Indices: [3026, 3637, 426, 691]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering.
        """
        # Step 1: Use FlexibleCustom to break down the problem into key reasoning steps
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step using extract_entities, find_connections, and synthesize_answer.",
            reasoning_pattern="sequential",
            steps=["extract_entities", "find_connections", "synthesize_answer"]
        )

        # Step 2: Generate a direct answer as a baseline
        baseline_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom result with the baseline
        solutions = [solution, baseline_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 4: Review the ensemble result for refinement
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution