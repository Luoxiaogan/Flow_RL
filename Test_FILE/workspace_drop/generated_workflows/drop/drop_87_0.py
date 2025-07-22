# Workflow ID: drop_87_0
# Benchmark: drop
# Data Indices: [2810, 2657, 2564, 3891, 2948]

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
        This is a workflow graph optimized for efficiency and appropriate operator usage.
        Uses specialized operators based on problem type without conditional logic.
        """
        # Generate direct answer as baseline
        direct_answer = await self.answer_generate()

        # Use counting reasoning if the task involves counting entities/events
        counting_result = await self.counting_reasoning()

        # Use arithmetic reasoning if numerical computation is required
        arithmetic_result = await self.arithmetic_reasoning()

        # Use comparison reasoning if max/min or comparison is needed
        comparison_result = await self.comparison_reasoning()

        # Ensemble all results to select best solution
        solutions = [direct_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution