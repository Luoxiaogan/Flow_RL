# Workflow ID: drop_38_0
# Benchmark: drop
# Data Indices: [3207, 183, 2569, 961]

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
        This is a comprehensive reasoning workflow for reading comprehension and discrete reasoning.
        It uses multiple specialized operators in parallel and sequentially to generate robust solutions.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        sequential_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Carefully count or calculate, then verify your result by checking for missed elements.",
            reasoning_pattern="iterative",
            steps=["initial_calculation", "check_completeness", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Ensembling all solutions to select the best one
        solutions = [initial_answer, sequential_analysis, iterative_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer