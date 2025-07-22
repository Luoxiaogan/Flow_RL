# Workflow ID: hotpotqa_325_0
# Benchmark: hotpotqa
# Data Indices: [3463, 14, 3206, 1995, 267]

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
        """
        # Step 1: Use FlexibleCustom with sequential pattern to trace multi-hop connections
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and reason through each step sequentially to find the answer.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        solution2 = await self.answer_generate()

        # Step 3: Review the initial flexible custom solution for refinement
        reviewed_solution = await self.review(pre_solution=solution1)

        # Step 4: Ensemble the two solutions (direct answer + refined multi-hop)
        ensemble_solution = await self.sc_ensemble(solutions=[solution2, reviewed_solution])

        return ensemble_solution