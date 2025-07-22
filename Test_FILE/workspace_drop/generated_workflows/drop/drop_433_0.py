# Workflow ID: drop_433_0
# Benchmark: drop
# Data Indices: [2553, 2293, 2446, 3714, 211]

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
        This is a comprehensive reasoning workflow that uses multiple operators to solve reading comprehension and discrete reasoning problems.
        It combines step-by-step breakdowns, specialized reasoning, and ensemble-based solution selection.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for detailed step-by-step breakdown
        step_by_step_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_information", "reason_step_by_step", "verify_conclusion"]
        )

        # Step 3: Use flexible custom with iterative pattern for refinement (e.g., counting or arithmetic)
        refined_solution = await self.flexible_custom(
            custom_instruction="Carefully count or calculate, then verify your result by checking for potential errors or missed elements.",
            reasoning_pattern="iterative",
            steps=["initial_calculation_or_count", "check_for_errors", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Ensembles the three solutions to select the best one
        ensemble_solutions = [initial_answer, step_by_step_solution, refined_solution]
        final_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_solution