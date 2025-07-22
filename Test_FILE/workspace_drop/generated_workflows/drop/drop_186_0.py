# Workflow ID: drop_186_0
# Benchmark: drop
# Data Indices: [847, 3506, 3485, 3790]

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
        It uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Use Custom to extract key elements (e.g., players, scores, events) from the passage
        extracted_info = await self.custom(instruction="Break down the passage into key events, players, and numerical values relevant to the question.")

        # Step 2: Use CountingReasoning if the problem involves counting entities or occurrences
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if the problem requires numerical computation
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning if the problem involves comparing values (e.g., max/min)
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate direct answer using AnswerGenerate as baseline
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble multiple solutions for higher accuracy
        solutions = [extracted_info, count_result, arithmetic_result, comparison_result, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution