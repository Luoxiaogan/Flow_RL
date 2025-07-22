# Workflow ID: drop_351_0
# Benchmark: drop
# Data Indices: [3807, 2152, 3726, 1061, 2329]

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
        This is a workflow graph optimized for comprehensive reasoning.
        Uses multiple specialized operators and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for step-by-step breakdown
        step_by_step_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["identify_key_elements", "extract_numerical_data", "apply_logical_rules", "derive_final_answer"]
        )

        # Step 3: Use flexible custom with iterative pattern to refine counting or arithmetic tasks
        refined_solution = await self.flexible_custom(
            custom_instruction="Carefully count or compute values, then verify your result by rechecking steps.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "verify_completeness", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Compare solutions using ScEnsemble to select best one
        solutions = [initial_answer, step_by_step_solution, refined_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer