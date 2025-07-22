# Workflow ID: drop_372_0
# Benchmark: drop
# Data Indices: [648, 2825, 386, 2970]

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
        It uses multiple operators in parallel and sequential patterns to ensure robust reasoning.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy improvement
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Carefully count or calculate, then verify your result by checking for missed elements",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "check_completeness", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Use comparison reasoning for problems involving comparisons (e.g., longest pass, highest score)
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [initial_answer, sequential_reasoning, iterative_refinement, comparison_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer