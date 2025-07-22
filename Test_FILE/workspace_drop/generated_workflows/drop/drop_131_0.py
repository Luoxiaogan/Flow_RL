# Workflow ID: drop_131_0
# Benchmark: drop
# Data Indices: [1717, 1349, 3338, 488]

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
        This is a workflow graph optimized for reading comprehension and discrete reasoning.
        It uses specialized operators based on problem type and combines them with ensemble and review.
        """
        # Step 1: Use Custom to break down the problem into steps
        initial_analysis = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Generate an answer directly as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: If the problem involves counting, use CountingReasoning
        count_result = await self.counting_reasoning()

        # Step 4: If arithmetic is needed, use ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If comparison is required, use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Step 6: Use FlexibleCustom for complex reasoning patterns (e.g., iterative refinement)
        refined_solution = await self.flexible_custom(
            custom_instruction="Break the problem into logical steps and refine iteratively",
            reasoning_pattern="iterative",
            steps=["extract_key_info", "identify_operation", "compute_step_by_step", "verify_final_answer"],
            max_iterations=3
        )

        # Step 7: Ensemble multiple solutions to select the best one
        solutions = [initial_analysis, direct_answer, count_result, arithmetic_result, comparison_result, refined_solution]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 8: Final review to improve the ensembled solution
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution