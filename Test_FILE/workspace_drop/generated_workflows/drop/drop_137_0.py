# Workflow ID: drop_137_0
# Benchmark: drop
# Data Indices: [3112, 3716, 1020, 366, 159]

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
        This is a workflow graph optimized for efficiency and clarity.
        Uses specialized operators based on problem type without conditional logic.
        """
        # Generate baseline answer
        base_answer = await self.answer_generate()

        # Get counting-based solution (for problems asking "how many")
        counting_solution = await self.counting_reasoning()

        # Get arithmetic solution (for numerical computations)
        arithmetic_solution = await self.arithmetic_reasoning()

        # Get comparison solution (for max/min or comparisons)
        comparison_solution = await self.comparison_reasoning()

        # Ensemble the three specialized solutions to improve accuracy
        ensemble_result = await self.sc_ensemble(solutions=[base_answer, counting_solution, arithmetic_solution, comparison_solution])

        # Final review step to refine the ensemble result
        final_answer = await self.review(pre_solution=ensemble_result)

        return final_answer