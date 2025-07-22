# Workflow ID: drop_436_0
# Benchmark: drop
# Data Indices: [1130, 3869, 2235, 3504, 1538]

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
        This is a workflow graph optimized for step-by-step reasoning.
        Uses specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Get initial answer using direct generation
        initial_answer = await self.answer_generate()

        # Step 2: Generate a step-by-step breakdown for clarity
        step_by_step = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 3: Use counting reasoning if applicable (e.g., "how many" questions)
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if numerical computation is needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if max/min or ranking is required
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all generated solutions to select the best one
        solutions = [initial_answer, step_by_step, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution