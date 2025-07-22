# Workflow ID: drop_419_0
# Benchmark: drop
# Data Indices: [1125, 3899, 1859, 2389]

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
        Uses flexible custom reasoning patterns and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use FlexibleCustom with sequential pattern for step-by-step breakdown
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into detailed steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_information", "reason_step_by_step", "verify_solution"]
        )

        # Step 3: Use FlexibleCustom with parallel pattern to explore multiple solution paths
        parallel_reasoning = await self.flexible_custom(
            custom_instruction="Explore multiple approaches to solving this problem independently and compare them.",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "compare_approaches"]
        )

        # Step 4: Use specialized operators for specific reasoning tasks (counting, arithmetic, comparison)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            sequential_reasoning,
            parallel_reasoning,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 6: Review the final answer for potential improvements
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer