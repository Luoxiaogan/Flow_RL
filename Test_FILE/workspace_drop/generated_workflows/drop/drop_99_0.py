# Workflow ID: drop_99_0
# Benchmark: drop
# Data Indices: [959, 1210, 2704, 1457, 2639]

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
        This is a workflow graph optimized for step-by-step reasoning using specialized operators.
        It combines multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Use Custom to extract and break down the problem into logical steps
        structured_analysis = await self.custom(instruction="Break down the problem into clear, logical steps with detailed reasoning for each.")

        # Step 2: Run direct answer generation as a baseline
        direct_answer = await self.answer_generate()

        # Step 3: Use specialized reasoning operators based on problem type (automatically detected internally)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensembling multiple solutions from different reasoning paths
        solutions = [
            structured_analysis,
            direct_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review of the ensemble result for clarity and correctness
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution