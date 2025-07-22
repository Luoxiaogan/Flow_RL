# Workflow ID: drop_232_0
# Benchmark: drop
# Data Indices: [2710, 2220, 3639, 1099]

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
        It uses multiple operators in parallel and sequential patterns to ensure robustness.
        """
        # Step 1: Generate initial answer using direct reasoning
        base_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps with clear reasoning for each",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_operations", "perform_calculation", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        refined_answer = await self.flexible_custom(
            custom_instruction="Carefully count or compute while double-checking for errors",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "verify_completeness", "refine_result"],
            max_iterations=3
        )

        # Step 4: Use specialized arithmetic reasoning for numerical tasks
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning for max/min or relative value problems
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [base_answer, step_by_step, refined_answer, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution