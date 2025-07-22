# Workflow ID: drop_2_0
# Benchmark: drop
# Data Indices: [2059, 1939, 2361, 658, 1274]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.agent = create(config)
        self.custom = operator.Custom(self.agent, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.agent, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.agent, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.agent, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.agent, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.agent, self.problem)

    async def run_workflow(self):
        """
        This is a robust workflow graph using Parallel Ensemble for enhanced accuracy.
        It generates multiple solutions via different reasoning paths, then selects the best one.
        """
        # Step 1: Generate multiple diverse solutions using different operators
        solution1 = await self.answer_generate()
        solution2 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solution3 = await self.counting_reasoning()
        solution4 = await self.arithmetic_reasoning()
        solution5 = await self.comparison_reasoning()

        # Step 2: Use ScEnsemble to select the most consistent answer from all generated solutions
        solutions = [solution1, solution2, solution3, solution4, solution5]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer