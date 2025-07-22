# Workflow ID: drop_60_0
# Benchmark: drop
# Data Indices: [979, 1833, 1313, 171, 2804]

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
        with flexible reasoning patterns to handle diverse reading comprehension and discrete reasoning tasks.
        """
        # Step 1: Use FlexibleCustom in sequential mode for structured step-by-step analysis
        sequential_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and reason through each one carefully",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logical_rules", "generate_answer"]
        )

        # Step 2: Generate a direct answer using AnswerGenerate for baseline
        direct_answer = await self.answer_generate()

        # Step 3: Review the direct answer to refine it
        reviewed_answer = await self.review(pre_solution=direct_answer)

        # Step 4: Use CountingReasoning if counting is needed (e.g., field goals, households)
        counting_result = await self.counting_reasoning()

        # Step 5: Use ArithmeticReasoning for numerical computations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: Use ComparisonReasoning for max/min or comparison questions
        comparison_result = await self.comparison_reasoning()

        # Step 7: Ensemble all results to select the best solution
        solutions = [
            sequential_analysis,
            reviewed_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution