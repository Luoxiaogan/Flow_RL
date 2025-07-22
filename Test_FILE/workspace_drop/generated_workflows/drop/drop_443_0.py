# Workflow ID: drop_443_0
# Benchmark: drop
# Data Indices: [1004, 2318, 371, 3630]

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
        This is a workflow graph optimized for step-by-step reasoning in reading comprehension and discrete reasoning tasks.
        Uses specialized operators based on task type and ensembles solutions where appropriate.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom reasoning for complex multi-step problems (e.g., comparisons or calculations)
        flex_answer = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and reason through each one carefully.",
            reasoning_pattern="sequential",
            steps=["extract_data", "identify_operation", "perform_calculation", "verify_result"]
        )

        # Step 4: Ensemble multiple reasoning paths to select the best solution
        solutions = [initial_answer, reviewed_answer, flex_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer