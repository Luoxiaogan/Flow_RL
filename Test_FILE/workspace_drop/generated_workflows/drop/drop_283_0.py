# Workflow ID: drop_283_0
# Benchmark: drop
# Data Indices: [370, 3067, 1937, 325, 1295]

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
        Uses multiple specialized operators and ensembles their results.
        """
        # Step 1: Generate base answer directly
        base_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        seq_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_relevant_info", "reason_step_by_step", "verify_solution"]
        )

        # Step 3: Use flexible custom with parallel reasoning to explore multiple approaches
        parallel_reasoning = await self.flexible_custom(
            custom_instruction="Explore multiple valid reasoning paths independently and compare them.",
            reasoning_pattern="parallel",
            steps=["approach_a", "approach_b", "compare_approaches"]
        )

        # Step 4: Review the base answer for potential improvements
        reviewed_answer = await self.review(pre_solution=base_answer)

        # Step 5: Ensemble all solutions to select the best one
        solutions = [base_answer, seq_reasoning, parallel_reasoning, reviewed_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution