# Workflow ID: drop_647_0
# Benchmark: drop
# Data Indices: [2987, 1656, 1448, 748]

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
        It uses step-by-step reasoning via Custom, specialized operators (Counting/Arithmetic/Comparison),
        and ensembles multiple solutions to improve robustness.
        """
        # Step 1: Extract key information using Custom with step-by-step instruction
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate an initial answer directly
        direct_answer = await self.answer_generate()

        # Step 3: Use specialized operators based on problem type (automatically detected)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble all solutions to select the best one
        solutions = [
            extracted_info,
            direct_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution