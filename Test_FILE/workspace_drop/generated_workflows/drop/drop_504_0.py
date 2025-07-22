# Workflow ID: drop_504_0
# Benchmark: drop
# Data Indices: [794, 587, 1319, 3910]

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
        # Step 1: Use CountingReasoning for counting tasks (e.g., "how many field goals between X and Y")
        count_solution = await self.counting_reasoning()

        # Step 2: Use ArithmeticReasoning for numerical computations (e.g., "how many more yards")
        arithmetic_solution = await self.arithmetic_reasoning()

        # Step 3: Use ComparisonReasoning for max/min or comparison tasks (e.g., "which event happened first")
        comparison_solution = await self.comparison_reasoning()

        # Step 4: Generate a direct answer as baseline
        baseline_answer = await self.answer_generate()

        # Step 5: Ensemble all solutions to pick the best one
        solutions = [count_solution, arithmetic_solution, comparison_solution, baseline_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer