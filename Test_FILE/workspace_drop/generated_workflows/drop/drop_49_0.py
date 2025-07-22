# Workflow ID: drop_49_0
# Benchmark: drop
# Data Indices: [3704, 3720, 685, 826, 660]

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
        It uses step-by-step reasoning with specialized operators based on task type.
        """
        # Step 1: Extract key information from the passage using Custom
        extracted_info = await self.custom(instruction="Break down the passage into relevant facts needed to answer the question.")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Use Review to refine the initial answer based on extracted info
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: If the problem involves counting, use CountingReasoning
        count_result = await self.counting_reasoning()

        # Step 5: If the problem involves arithmetic, use ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: If the problem involves comparison, use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Step 7: Ensemble all solutions to select the best one
        solutions = [refined_answer, count_result, arithmetic_result, comparison_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer