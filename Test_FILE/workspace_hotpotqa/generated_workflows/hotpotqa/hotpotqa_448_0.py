# Workflow ID: hotpotqa_448_0
# Benchmark: hotpotqa
# Data Indices: [2376, 1841, 554, 1981]

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
        This is a workflow graph for multi-hop question answering using sequential reasoning.
        It breaks down the problem step-by-step and ensembles multiple solutions for robustness.
        """
        # Step 1: Use FlexibleCustom to perform sequential multi-hop reasoning
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each connection sequentially.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate a direct answer for comparison
        solution2 = await self.answer_generate()

        # Step 3: Review the first solution to refine it
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (original and reviewed) to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[solution1, reviewed_solution, solution2])

        return ensemble_solution