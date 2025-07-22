# Workflow ID: drop_65_0
# Benchmark: drop
# Data Indices: [764, 276, 3181, 3078]

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
        This is a workflow graph optimized for efficiency and correctness.
        Uses specialized operators based on problem type without conditional logic.
        """
        # Generate base answer using direct reasoning
        base_answer = await self.answer_generate()

        # Try counting reasoning if the problem involves counts
        count_solution = await self.counting_reasoning()

        # Try arithmetic reasoning if the problem involves calculations
        arithmetic_solution = await self.arithmetic_reasoning()

        # Try comparison reasoning if the problem compares values
        comparison_solution = await self.comparison_reasoning()

        # Ensemble all solutions to pick the best one
        solutions = [base_answer, count_solution, arithmetic_solution, comparison_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer