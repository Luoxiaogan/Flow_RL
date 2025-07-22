# Workflow ID: drop_190_0
# Benchmark: drop
# Data Indices: [784, 3152, 436, 1343]

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
        This is a workflow graph optimized for step-by-step reasoning.
        Uses specialized operators based on problem type and ensembles results.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom for structured step-by-step breakdown
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_operation", "perform_stepwise_calculation", "verify_solution"]
        )

        # Step 3: If the problem involves counting, use dedicated counting reasoning
        counting_result = await self.counting_reasoning()

        # Step 4: If the problem involves arithmetic operations, use arithmetic reasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If comparison is needed (e.g., max/min), use comparison reasoning
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to find the best one
        solutions = [
            initial_answer,
            structured_reasoning,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution