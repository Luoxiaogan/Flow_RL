# Workflow ID: drop_532_0
# Benchmark: drop
# Data Indices: [2786, 3075, 1615, 1585]

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
        This is a workflow graph optimized for reading comprehension and discrete reasoning.
        Uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Extract key information using Custom reasoning (step-by-step breakdown)
        step_by_step_analysis = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 2: Generate direct answer from the problem
        direct_answer = await self.answer_generate()

        # Step 3: Use counting reasoning if the problem involves counting entities or events
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if numerical computation is needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if the problem requires finding max/min or comparing values
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [
            step_by_step_analysis,
            direct_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution