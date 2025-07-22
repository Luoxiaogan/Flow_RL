# Workflow ID: drop_447_0
# Benchmark: drop
# Data Indices: [2911, 339, 308, 1838, 127]

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
        Uses specialized operators based on problem type and ensembles multiple solutions for robustness.
        """
        # Step 1: Use Custom to extract key facts from the passage
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and identify all relevant numerical or comparative data points.")

        # Step 2: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Run specialized reasoning operators based on likely problem types
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble all results to select the best solution
        solutions = [initial_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Optional review to refine the final answer
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution