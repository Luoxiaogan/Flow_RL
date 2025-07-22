# Workflow ID: drop_882_0
# Benchmark: drop
# Data Indices: [1286, 1584, 983, 1059, 3387]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.problem_text = str(problem) if isinstance(problem, dict) else problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.config, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.config, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a comprehensive reasoning workflow for reading comprehension and discrete reasoning.
        It uses multiple specialized operators and ensembles the best result.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step verification
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into detailed steps and explain each reasoning step clearly",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_operation", "perform_calculation", "verify_result"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy improvement
        iter_solution = await self.flexible_custom(
            custom_instruction="Carefully count or compute, then verify for completeness",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "cross_check", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Review the initial answer to improve clarity and correctness
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 5: Ensemble all solutions to select the best one
        solutions = [initial_answer, seq_solution, iter_solution, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer