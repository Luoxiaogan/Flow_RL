# Workflow ID: drop_522_0
# Benchmark: drop
# Data Indices: [2908, 3321, 180, 2361]

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
        This is a comprehensive reasoning workflow that combines multiple specialized operators
        and uses FlexibleCustom for structured reasoning patterns.
        """
        # Step 1: Use flexible custom with sequential reasoning to break down the problem step-by-step
        solution_step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_information", "apply_logic", "verify_solution"]
        )

        # Step 2: Generate a direct answer using AnswerGenerate
        direct_answer = await self.answer_generate()

        # Step 3: Use Review to refine the previous solution
        reviewed_solution = await self.review(pre_solution=solution_step_by_step)

        # Step 4: Ensemble multiple solutions (step-by-step + direct + reviewed)
        ensemble_solutions = [solution_step_by_step, direct_answer, reviewed_solution]
        final_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_solution