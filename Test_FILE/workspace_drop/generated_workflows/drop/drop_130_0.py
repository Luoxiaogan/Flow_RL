# Workflow ID: drop_130_0
# Benchmark: drop
# Data Indices: [382, 1928, 2941, 1972]

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
        This is a comprehensive workflow graph for reading comprehension and discrete reasoning.
        It uses multiple reasoning strategies (sequential, parallel, iterative) with ensemble selection.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for step-by-step verification
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and explain each reasoning phase.",
            reasoning_pattern="sequential",
            steps=["extract_key_data", "identify_operation", "perform_calculation", "verify_result"]
        )

        # Step 3: Use flexible custom with iterative pattern to refine counting or arithmetic results
        iterative_solution = await self.flexible_custom(
            custom_instruction="Refine your answer by checking for missing elements or errors in calculation.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "check_completeness", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Use specialized operators for domain-specific tasks
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solution_list = [
            initial_answer,
            sequential_solution,
            iterative_solution,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 6: Review the final solution for clarity and correctness
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution