# Workflow ID: drop_785_0
# Benchmark: drop
# Data Indices: [799, 975, 34, 1280, 2391]

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
        Uses step-by-step reasoning via specialized operators and ensembles multiple solutions.
        """
        # Step 1: Use Custom to extract key information from the passage
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and identify all relevant numerical or categorical data.")

        # Step 2: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Use specialized operators based on problem type (no conditionals — let operators handle it)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [
            direct_answer,
            extracted_info,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Optional review to refine the best solution
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution