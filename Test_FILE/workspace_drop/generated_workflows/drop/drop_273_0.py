# Workflow ID: drop_273_0
# Benchmark: drop
# Data Indices: [3177, 3597, 2729, 3052, 2712]

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
        It uses multiple specialized operators in sequence and parallel to generate robust solutions.
        """
        # Step 1: Generate an initial answer using direct reasoning
        base_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for detailed step-by-step breakdown
        detailed_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logic", "validate_solution"]
        )

        # Step 3: Use flexible custom with parallel pattern to explore multiple solution paths
        parallel_solutions = await self.flexible_custom(
            custom_instruction="Explore different approaches to solve the problem independently.",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "approach_c"]
        )

        # Step 4: Ensemble all generated solutions to select the best one
        solutions_list = [base_answer, detailed_reasoning, parallel_solutions]
        final_answer = await self.sc_ensemble(solutions=solutions_list)

        # Step 5: Review the final answer to ensure correctness and clarity
        refined_answer = await self.review(pre_solution=final_answer)

        return refined_answer