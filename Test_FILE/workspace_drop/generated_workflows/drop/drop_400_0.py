# Workflow ID: drop_400_0
# Benchmark: drop
# Data Indices: [3699, 1183, 716, 2959, 3660]

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
        It uses multiple reasoning strategies to enhance robustness and accuracy.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for detailed step-by-step breakdown
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and explain each reasoning step thoroughly.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_task_type", "apply_logic_step_by_step", "validate_result"]
        )

        # Step 3: Use flexible custom with iterative refinement for counting or arithmetic tasks
        iterative_solution = await self.flexible_custom(
            custom_instruction="Carefully count or compute the result, then verify for completeness and correctness.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "compute_result", "verify_accuracy"],
            max_iterations=2
        )

        # Step 4: Use parallel approach to generate alternative interpretations
        parallel_solution = await self.flexible_custom(
            custom_instruction="Consider multiple perspectives or solution paths for this problem.",
            reasoning_pattern="parallel",
            steps=["generate_alternate_approach", "evaluate_consistency", "select_best"]
        )

        # Step 5: Ensembling all solutions to pick the best one
        solutions = [initial_answer, sequential_solution, iterative_solution, parallel_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer