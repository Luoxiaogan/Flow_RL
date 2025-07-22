# Workflow ID: drop_82_0
# Benchmark: drop
# Data Indices: [2635, 1248, 3585, 2940]

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
        Uses multiple operators in sequence and ensemble to ensure robustness.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for detailed step-by-step breakdown
        detailed_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "formulate_answer"]
        )

        # Step 3: Review the initial answer for potential improvements
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 4: Generate a solution using specialized counting if applicable
        counting_result = await self.counting_reasoning()

        # Step 5: Generate a solution using specialized arithmetic if applicable
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: Generate a solution using specialized comparison if applicable
        comparison_result = await self.comparison_reasoning()

        # Step 7: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            detailed_reasoning,
            reviewed_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer