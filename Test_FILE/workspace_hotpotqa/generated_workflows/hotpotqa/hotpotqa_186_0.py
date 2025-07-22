# Workflow ID: hotpotqa_186_0
# Benchmark: hotpotqa
# Data Indices: [2815, 3181, 10, 1170]

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
        It first breaks down the problem step-by-step, then refines the solution through review,
        and finally ensembles multiple reasoning paths to improve accuracy.
        """
        # Step 1: Use flexible custom with sequential reasoning to trace multi-hop connections
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and trace connections between pieces of information.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_reasoning_path", "synthesize_final_answer"]
        )

        # Step 2: Generate an alternative answer directly for comparison
        direct_answer = await self.answer_generate()

        # Step 3: Review the sequential solution to refine it
        refined_solution = await self.review(pre_solution=sequential_solution)

        # Step 4: Ensemble the direct answer and refined solution to select the best one
        final_solution = await self.sc_ensemble(solutions=[direct_answer, refined_solution])

        return final_solution