# Workflow ID: drop_129_0
# Benchmark: drop
# Data Indices: [3342, 2275, 3659, 2606, 1409]

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
        This is a robust workflow graph using Parallel Ensemble for enhanced accuracy.
        Generates multiple solutions via different reasoning paths, then selects the best one.
        """
        # Generate diverse solutions using different specialized operators
        solution1 = await self.answer_generate()
        solution2 = await self.custom(instruction="Break down the problem step-by-step with clear reasoning for each part.")
        solution3 = await self.counting_reasoning()
        solution4 = await self.arithmetic_reasoning()
        solution5 = await self.comparison_reasoning()

        # Ensemble all solutions to find the most consistent and accurate answer
        solutions = [solution1, solution2, solution3, solution4, solution5]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer