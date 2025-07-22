# Workflow ID: drop_556_0
# Benchmark: drop
# Data Indices: [387, 1706, 3367, 3995, 2373]

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
        It uses step-by-step reasoning with specialized operators based on problem type.
        """
        # Step 1: Extract key information using Custom (step-by-step breakdown)
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Use ComparisonReasoning if comparison is needed (e.g., "which is lower")
        comparison_result = await self.comparison_reasoning()

        # Step 4: Use CountingReasoning if counting is required (e.g., "how many touchdowns")
        counting_result = await self.counting_reasoning()

        # Step 5: Use ArithmeticReasoning if numerical computation is needed (e.g., "how many more yards")
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: Ensemble multiple solutions to improve accuracy
        solutions = [initial_answer, comparison_result, counting_result, arithmetic_result]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 7: Final review to refine the answer
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer