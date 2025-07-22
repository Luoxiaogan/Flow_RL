# Workflow ID: drop_21_0
# Benchmark: drop
# Data Indices: [303, 814, 1899, 3819, 2918]

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
        This is a workflow graph optimized for reading comprehension and discrete reasoning.
        It uses specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Get initial answer from direct generation
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom to perform structured reasoning (sequential steps)
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step with clear reasoning",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logic_or_calculation", "verify_solution"]
        )

        # Step 3: Generate an alternative solution using Custom for different perspective
        alternative_answer = await self.custom(
            instruction="Solve this problem by breaking it down into smaller steps and explaining each reasoning step clearly"
        )

        # Step 4: Ensemble the three solutions to select the best one
        solutions = [initial_answer, structured_reasoning, alternative_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer