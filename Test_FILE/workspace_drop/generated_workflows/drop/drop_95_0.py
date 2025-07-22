# Workflow ID: drop_95_0
# Benchmark: drop
# Data Indices: [1272, 2411, 1655, 2787]

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
        This is a workflow graph optimized for step-by-step reasoning in reading comprehension and discrete tasks.
        Uses specialized operators based on problem type and ensembles multiple solutions for robustness.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use custom reasoning to break down the problem into steps (general purpose)
        step_by_step_analysis = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 3: Use counting reasoning if the task involves counting entities or events
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning for numerical calculations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning for max/min or relative value problems
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all results to select the best solution
        solutions = [
            initial_answer,
            step_by_step_analysis,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution