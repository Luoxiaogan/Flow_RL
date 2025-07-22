# Workflow ID: drop_353_0
# Benchmark: drop
# Data Indices: [575, 2080, 651, 1970]

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
        It uses specialized operators based on problem type and combines them with ensemble and review for robustness.
        """
        # Step 1: Use custom to extract key information from the passage in a structured way
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and identify all relevant numerical or comparative data points.")

        # Step 2: Generate direct answer as baseline
        direct_answer = await self.answer_generate()

        # Step 3: Use specialized reasoning operators based on problem type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for better accuracy
        solutions = [
            direct_answer,
            counting_result,
            arithmetic_result,
            comparison_result,
            extracted_info
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensembled solution for refinement
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution