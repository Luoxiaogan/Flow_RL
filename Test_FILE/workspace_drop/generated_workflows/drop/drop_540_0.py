# Workflow ID: drop_540_0
# Benchmark: drop
# Data Indices: [2282, 2939, 363, 3223, 741]

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
        # Step 1: Extract key information via custom reasoning
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate direct answer (for baseline)
        direct_answer = await self.answer_generate()

        # Step 3: Use counting reasoning if applicable (e.g., count occurrences, items)
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if numerical computation needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning for max/min or relative values
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all results to select best solution
        solutions = [extracted_info, direct_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution