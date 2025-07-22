# Workflow ID: hotpotqa_265_0
# Benchmark: hotpotqa
# Data Indices: [1228, 3872, 2698, 2823, 3851]

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
        It uses multiple reasoning paths and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct generation
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to break down the problem
        seq_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each step clearly.",
            reasoning_pattern="sequential",
            steps=["identify_key_entities", "find_intermediate_connections", "trace_logical_path", "synthesize_final_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement for deeper reasoning
        iter_refinement = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis, then verify facts and refine your answer iteratively.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_evidence", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Use Custom with detailed step-by-step instruction for another path
        detailed_step_by_step = await self.custom(
            instruction="Solve this by breaking it down into detailed steps and explaining the reasoning behind each step."
        )

        # Step 5: Ensemble the three solutions to select the best one
        solutions = [direct_answer, seq_reasoning, iter_refinement, detailed_step_by_step]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Final review of the ensembled solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer