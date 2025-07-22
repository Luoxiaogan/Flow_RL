# Workflow ID: drop_666_0
# Benchmark: drop
# Data Indices: [85, 3959, 3526, 1404]

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
        Uses multiple specialized operators and ensemble techniques to ensure robustness.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for step-by-step verification
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logic_step_by_step", "verify_conclusion"]
        )

        # Step 3: Use flexible custom with iterative pattern for refinement
        iterative_solution = await self.flexible_custom(
            custom_instruction="Carefully count or calculate, then verify your result by re-evaluating key elements.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "check_for_errors", "refine_result"],
            max_iterations=2
        )

        # Step 4: Use specialized operators for domain-specific tasks (counting, arithmetic, comparison)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            sequential_solution,
            iterative_solution,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer