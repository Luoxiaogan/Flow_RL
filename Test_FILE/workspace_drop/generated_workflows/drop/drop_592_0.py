# Workflow ID: drop_592_0
# Benchmark: drop
# Data Indices: [327, 3577, 2380, 2607]

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
        This is a workflow graph using Parallel Ensemble for robustness.
        Generates multiple solutions via different reasoning approaches,
        then selects the best one using sc_ensemble.
        """
        # Generate multiple solutions using different reasoning strategies
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")
        
        solution3 = await self.counting_reasoning()
        
        solution4 = await self.arithmetic_reasoning()
        
        solution5 = await self.comparison_reasoning()
        
        # Use flexible custom to explore multiple reasoning paths in parallel
        solution6 = await self.flexible_custom(
            custom_instruction="Use parallel reasoning: evaluate all possible interpretations of the question.",
            reasoning_pattern="parallel",
            steps=["identify_key_data", "extract_values", "compute_options", "compare_results"]
        )

        # Collect all solutions for ensemble
        solutions = [solution1, solution2, solution3, solution4, solution5, solution6]
        
        # Select the most consistent answer
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer