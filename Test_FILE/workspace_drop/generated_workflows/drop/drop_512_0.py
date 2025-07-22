# Workflow ID: drop_512_0
# Benchmark: drop
# Data Indices: [3723, 1734, 3781, 856]

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
        # Step 1: Generate an initial answer using direct reasoning
        solution1 = await self.answer_generate()

        # Step 2: Use Custom to break down the problem into steps for clearer reasoning
        solution2 = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")

        # Step 3: Use Counting/Arithmetic/Comparison reasoning based on problem type (automatically detected)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble all solutions to select the best one
        solutions = [solution1, solution2, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution