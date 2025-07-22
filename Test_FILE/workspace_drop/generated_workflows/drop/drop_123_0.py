# Workflow ID: drop_123_0
# Benchmark: drop
# Data Indices: [1666, 3160, 3206, 1326]

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
        This is a workflow graph optimized for step-by-step reasoning in reading comprehension and discrete reasoning.
        It uses specialized operators based on task type and ensembles multiple solutions to improve accuracy.
        """
        # Step 1: Use Custom to extract key details from the passage in a structured way
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step clearly.")

        # Step 2: Use CountingReasoning if the question involves counting events or items
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if the question involves numerical computation
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning if the question requires finding max/min or comparing values
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 6: Review the initial answer to refine it
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 7: Ensemble multiple solutions (from custom, count, arithmetic, comparison, and reviewed answers)
        solutions = [
            extracted_info,
            count_result,
            arithmetic_result,
            comparison_result,
            reviewed_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution