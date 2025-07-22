# Workflow ID: drop_199_0
# Benchmark: drop
# Data Indices: [1262, 3069, 789, 3589]

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
        This is a robust workflow graph using Parallel Ensemble pattern.
        Generates multiple solutions via different reasoning approaches, then ensembles the best one.
        """
        # Generate multiple independent solutions using different operators
        solution1 = await self.answer_generate()
        solution2 = await self.counting_reasoning()
        solution3 = await self.arithmetic_reasoning()
        solution4 = await self.comparison_reasoning()
        
        # Use flexible custom for a structured, step-by-step approach as a fifth solution
        solution5 = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and reason through each carefully",
            reasoning_pattern="sequential",
            steps=["extract_values", "identify_operation", "perform_calculation", "verify_result"]
        )

        # Ensemblers all solutions to find the most consistent and accurate answer
        solutions = [solution1, solution2, solution3, solution4, solution5]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer