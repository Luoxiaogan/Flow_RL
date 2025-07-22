# Workflow ID: drop_295_0
# Benchmark: drop
# Data Indices: [2772, 3663, 2018, 1042]

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
        This is a comprehensive reasoning workflow that uses multiple operators in parallel and sequentially to solve reading comprehension and discrete reasoning problems.
        """
        # Step 1: Use FlexibleCustom with sequential pattern for structured step-by-step analysis
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and reason through each one carefully.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logical_steps", "verify_conclusion"]
        )

        # Step 2: Generate direct answer using AnswerGenerate
        direct_answer = await self.answer_generate()

        # Step 3: Use CountingReasoning for counting tasks (if applicable)
        counting_result = await self.counting_reasoning()

        # Step 4: Use ArithmeticReasoning for numerical calculations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use ComparisonReasoning for max/min or comparative reasoning
        comparison_result = await self.comparison_reasoning()

        # Step 6: Use Custom to generate an alternative detailed explanation
        detailed_explanation = await self.custom(
            instruction="Explain the solution in detail, step by step, with clear reasoning for each part."
        )

        # Step 7: Ensemble all solutions to select the best one
        solutions = [seq_solution, direct_answer, counting_result, arithmetic_result, comparison_result, detailed_explanation]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer