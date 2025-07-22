# Workflow ID: drop_192_0
# Benchmark: drop
# Data Indices: [3290, 3194, 3018, 3056, 1328]

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
        This is a workflow graph optimized for comprehensive reasoning.
        Uses sequential and parallel reasoning patterns with ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly",
            reasoning_pattern="sequential",
            steps=["identify_key_elements", "extract_numerical_data", "perform_calculation_or_comparison", "verify_final_answer"]
        )

        # Step 3: Use flexible custom with parallel reasoning to explore multiple solution paths
        parallel_solution = await self.flexible_custom(
            custom_instruction="Explore multiple possible approaches to solve this problem",
            reasoning_pattern="parallel",
            steps=["approach_one", "approach_two", "compare_results", "select_best"]
        )

        # Step 4: Use specialized operators for focused reasoning
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            sequential_solution,
            parallel_solution,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Review the final solution for refinement
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution