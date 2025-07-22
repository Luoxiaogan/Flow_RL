# Workflow ID: drop_166_0
# Benchmark: drop
# Data Indices: [3360, 830, 3100, 1868]

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
        This is a robust workflow graph using Parallel Ensemble for enhanced accuracy.
        It generates multiple reasoning paths and selects the best solution via ensemble.
        """
        # Generate multiple solutions using different approaches
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Break down the problem step by step and explain each reasoning step clearly.")
        
        solution3 = await self.counting_reasoning()
        
        solution4 = await self.arithmetic_reasoning()
        
        solution5 = await self.comparison_reasoning()
        
        # Use flexible custom to explore alternative reasoning patterns
        solution6 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to solve the problem carefully.",
            reasoning_pattern="sequential",
            steps=["identify_key_data", "extract_values", "perform_calculation", "verify_result"]
        )
        
        # Ensemble all solutions to select the most consistent one
        solutions = [solution1, solution2, solution3, solution4, solution5, solution6]
        final_solution = await self.sc_ensemble(solutions=solutions)
        
        return final_solution