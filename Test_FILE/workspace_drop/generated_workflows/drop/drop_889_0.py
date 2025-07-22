# Workflow ID: drop_889_0
# Benchmark: drop
# Data Indices: [909, 2575, 1678, 2779]

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
        This is a robust workflow graph using Parallel Ensemble to generate multiple solutions.
        Each solution uses a different reasoning approach (direct generation, counting, arithmetic, comparison, custom step-by-step).
        Then we ensemble them to pick the most consistent answer.
        """
        # Generate multiple independent solutions using different operators
        solution1 = await self.answer_generate()
        solution2 = await self.counting_reasoning()
        solution3 = await self.arithmetic_reasoning()
        solution4 = await self.comparison_reasoning()
        solution5 = await self.custom(instruction="Break down the problem into smaller steps and explain your reasoning for each step.")

        # Collect all solutions for ensemble
        solutions = [solution1, solution2, solution3, solution4, solution5]

        # Use ScEnsemble to select the best solution based on consistency
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer