# Workflow ID: hotpotqa_172_0
# Benchmark: hotpotqa
# Data Indices: [3049, 2276, 1227, 2019, 2190]

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
        It breaks down the problem into smaller steps and connects information across different sources.
        """
        # Step 1: Use FlexibleCustom with sequential reasoning to trace connections step-by-step
        solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of evidence.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_answer"]
        )

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Ensemble the flexible custom solution and direct answer
        ensemble_solution = await self.sc_ensemble(solutions=[solution, direct_answer])

        # Step 4: Review the ensembled solution to refine it
        final_answer = await self.review(pre_solution=ensemble_solution)

        return final_answer