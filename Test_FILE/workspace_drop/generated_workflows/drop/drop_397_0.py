# Workflow ID: drop_397_0
# Benchmark: drop
# Data Indices: [727, 1029, 1452, 3312, 2658]

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
        # Step 1: Use Custom to extract key information from the passage in structured steps
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps. Identify all relevant numerical data, events, and relationships mentioned in the passage.")

        # Step 2: Use CountingReasoning for counting-related questions (e.g., touchdowns, field goals)
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning for numerical computations (e.g., point differences, totals)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning for comparing values or categories (e.g., ancestry, scores)
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate a direct answer using AnswerGenerate as baseline
        base_answer = await self.answer_generate()

        # Step 6: Ensemble multiple solutions to select the best one
        solutions = [extracted_info, count_result, arithmetic_result, comparison_result, base_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer