# Workflow ID: drop_200_0
# Benchmark: drop
# Data Indices: [1861, 500, 138, 480, 3833]

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
        It uses multiple operators in parallel and sequentially to ensure robustness and accuracy.
        """
        # Step 1: Generate an initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for detailed step-by-step breakdown
        step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "reason_step_by_step", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for critical checks
        refined_answer = await self.flexible_custom(
            custom_instruction="Refine your answer by double-checking all details and ensuring completeness.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "identify_gaps", "refine_conclusion"],
            max_iterations=2
        )

        # Step 4: Use specialized operators for specific tasks (counting, arithmetic, comparison)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            direct_answer,
            step_by_step,
            refined_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution