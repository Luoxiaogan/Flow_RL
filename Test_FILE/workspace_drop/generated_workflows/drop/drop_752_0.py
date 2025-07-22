# Workflow ID: drop_752_0
# Benchmark: drop
# Data Indices: [2374, 1312, 1154, 3034]

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
        This is a workflow graph optimized for step-by-step reasoning.
        Uses specialized operators based on problem type and ensembles results when needed.
        """
        # Step 1: Use Custom to break down the problem into steps
        initial_analysis = await self.custom(instruction="Break down the problem into smaller, clear steps with detailed reasoning for each.")

        # Step 2: Use ArithmeticReasoning if the problem involves numerical computation
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 3: Use ComparisonReasoning if the problem involves finding max/min or comparing values
        comparison_result = await self.comparison_reasoning()

        # Step 4: Use CountingReasoning if the problem requires counting entities or events
        counting_result = await self.counting_reasoning()

        # Step 5: Generate a direct answer using AnswerGenerate
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble multiple solutions to improve accuracy
        solutions = [initial_analysis, arithmetic_result, comparison_result, counting_result, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution