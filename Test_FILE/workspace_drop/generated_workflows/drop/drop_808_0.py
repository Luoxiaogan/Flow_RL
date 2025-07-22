# Workflow ID: drop_808_0
# Benchmark: drop
# Data Indices: [1289, 1589, 1051, 3400]

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
        This is a robust workflow graph using parallel ensemble for improved accuracy.
        Generates multiple reasoning paths and selects the best solution via ScEnsemble.
        """
        # Generate multiple solutions using different reasoning strategies
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")
        
        solution3 = await self.counting_reasoning()
        
        solution4 = await self.arithmetic_reasoning()
        
        solution5 = await self.comparison_reasoning()
        
        # Use flexible custom to explore an alternative reasoning path (parallel approach)
        solution6 = await self.flexible_custom(
            custom_instruction="Apply a sequential reasoning pattern with verification at each step.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_operation", "perform_calculation", "verify_result"]
        )

        # Ensemble all solutions to find the most consistent answer
        solutions = [solution1, solution2, solution3, solution4, solution5, solution6]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer