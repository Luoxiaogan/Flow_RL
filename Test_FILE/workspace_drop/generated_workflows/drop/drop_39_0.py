# Workflow ID: drop_39_0
# Benchmark: drop
# Data Indices: [534, 2958, 1113, 119, 1269]

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
        It uses step-by-step reasoning with specialized operators based on problem type.
        """
        # Step 1: Use Custom to extract key information from the passage in a structured way
        extracted_info = await self.custom(instruction="Break down the passage into relevant facts that help answer the question. Focus on identifying entities, actions, and numerical values.")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Use Review to refine the initial answer based on extracted info
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 4: For problems involving counting, use CountingReasoning
        count_result = await self.counting_reasoning()

        # Step 5: For problems requiring arithmetic operations, use ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: For problems needing comparisons (e.g., max/min), use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Step 7: Ensemble all results to select the best solution
        solutions = [refined_answer, count_result, arithmetic_result, comparison_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer