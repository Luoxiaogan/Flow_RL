# Workflow ID: drop_821_0
# Benchmark: drop
# Data Indices: [3866, 2744, 3153, 3901]

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
        It uses step-by-step reasoning via specialized operators and ensembles results when appropriate.
        """
        # Step 1: Extract key information using Custom reasoning (step-by-step breakdown)
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Use CountingReasoning if the task involves counting entities or events
        counting_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if numerical computation is needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning if comparing values or finding max/min is required
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate a direct answer using AnswerGenerate
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble multiple solutions to improve robustness
        ensemble_solution = await self.sc_ensemble(
            solutions=[
                extracted_info,
                counting_result,
                arithmetic_result,
                comparison_result,
                direct_answer
            ]
        )

        # Step 7: Final review of the ensembled solution to refine accuracy
        final_solution = await self.review(pre_solution=ensemble_solution)

        return final_solution