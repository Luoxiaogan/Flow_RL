# Workflow ID: drop_495_0
# Benchmark: drop
# Data Indices: [2867, 993, 1700, 2803, 817]

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
        This is a workflow graph using Parallel Ensemble for robustness.
        Generates multiple solutions via different reasoning approaches and ensembles them.
        """
        # Generate diverse solutions using different operators
        solution1 = await self.answer_generate()
        solution2 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        solution3 = await self.counting_reasoning()
        solution4 = await self.arithmetic_reasoning()
        solution5 = await self.comparison_reasoning()

        # Use ScEnsemble to select the best solution from the list
        ensemble_result = await self.sc_ensemble(solutions=[
            solution1, solution2, solution3, solution4, solution5
        ])

        return ensemble_result