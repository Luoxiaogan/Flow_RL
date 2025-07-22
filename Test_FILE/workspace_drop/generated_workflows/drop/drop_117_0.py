# Workflow ID: drop_117_0
# Benchmark: drop
# Data Indices: [1275, 620, 3774, 3604]

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
        It uses multiple reasoning strategies (sequential, iterative, parallel) and ensembles results.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern to break down the problem step-by-step
        step_by_step_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_information", "apply_logic", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative pattern for refinement
        refined_answer = await self.flexible_custom(
            custom_instruction="Carefully count or calculate, then verify your result by checking for completeness and accuracy.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "verify_accuracy", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Use specialized operators for specific tasks
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            step_by_step_solution,
            refined_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Review the final solution for clarity and correctness
        final_answer = await self.review(pre_solution=final_solution)

        return final_answer