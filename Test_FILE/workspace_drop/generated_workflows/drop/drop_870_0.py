# Workflow ID: drop_870_0
# Benchmark: drop
# Data Indices: [1975, 3580, 426, 3327, 2466]

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
        This is a robust workflow graph using Parallel Ensemble pattern.
        Generates multiple solutions via different reasoning paths, then ensembles the best one.
        """
        # Generate diverse solutions using different specialized operators
        solution1 = await self.answer_generate()
        solution2 = await self.counting_reasoning()
        solution3 = await self.arithmetic_reasoning()
        solution4 = await self.comparison_reasoning()

        # Use Custom to generate a step-by-step reasoned solution
        solution5 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Create a list of solutions for ensemble
        solutions = [solution1, solution2, solution3, solution4, solution5]

        # Ensemble to select the most consistent and accurate answer
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer