# Workflow ID: drop_150_0
# Benchmark: drop
# Data Indices: [1581, 3293, 1825, 2150]

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
        This is a comprehensive reasoning workflow that combines multiple operators
        to handle diverse reading comprehension and discrete reasoning tasks.
        """
        # Step 1: Use flexible custom with sequential reasoning for structured step-by-step analysis
        solution_seq = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_relevant_info", "apply_logic_or_calculation", "verify_solution"]
        )

        # Step 2: Generate a direct answer using AnswerGenerate for baseline
        direct_answer = await self.answer_generate()

        # Step 3: Use counting-specific reasoning if applicable (e.g., for count-based questions)
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic-specific reasoning if numerical computation needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison-specific reasoning if max/min or relative values are required
        comparison_result = await self.comparison_reasoning()

        # Step 6: Review the best solution from earlier steps
        reviewed_solution = await self.review(pre_solution=solution_seq)

        # Step 7: Ensemble all solutions to select the most accurate one
        ensemble_solutions = [direct_answer, solution_seq, counting_result, arithmetic_result, comparison_result, reviewed_solution]
        final_answer = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_answer