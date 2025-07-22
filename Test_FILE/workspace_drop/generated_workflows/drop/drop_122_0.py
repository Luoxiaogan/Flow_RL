# Workflow ID: drop_122_0
# Benchmark: drop
# Data Indices: [3394, 1625, 2905, 3797]

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
        and uses ensemble techniques to improve accuracy.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        step_by_step_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step carefully.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_result"]
        )

        # Step 3: Use flexible custom with iterative refinement for precision
        refined_answer = await self.flexible_custom(
            custom_instruction="Carefully count or calculate, then refine your answer by double-checking all steps.",
            reasoning_pattern="iterative",
            steps=["initial_calculation", "check_for_errors", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Ensemple the three solutions (initial, step-by-step, refined) to select best
        solutions = [initial_answer, step_by_step_solution, refined_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer