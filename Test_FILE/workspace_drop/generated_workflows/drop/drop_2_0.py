# Workflow ID: drop_2_0
# Benchmark: drop
# Data Indices: [3008, 3041, 3918, 3378, 3081]

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
        This is a workflow graph optimized for step-by-step reasoning and ensemble-based accuracy.
        Uses specialized operators based on problem type, with custom reasoning steps to guide thinking.
        """
        # Step 1: Use Custom to extract and break down the problem into logical steps
        reasoning_step = await self.custom(instruction="Break down the problem into clear, logical steps. Identify what needs to be counted, calculated, or compared.")
        
        # Step 2: Use flexible_custom to apply structured reasoning (sequential pattern) for complex problems
        structured_solution = await self.flexible_custom(
            custom_instruction="Apply sequential reasoning: identify key data points, determine required operations, compute step by step, and verify the result.",
            reasoning_pattern="sequential",
            steps=["identify_values", "determine_operation", "perform_calculation", "verify_result"]
        )
        
        # Step 3: If the problem involves counting, use CountingReasoning for precision
        count_solution = await self.counting_reasoning()
        
        # Step 4: If the problem involves arithmetic, use ArithmeticReasoning for accurate computation
        arithmetic_solution = await self.arithmetic_reasoning()
        
        # Step 5: If the problem involves comparisons (max/min, ratios, etc.), use ComparisonReasoning
        comparison_solution = await self.comparison_reasoning()
        
        # Step 6: Generate a direct answer using AnswerGenerate as baseline
        baseline_answer = await self.answer_generate()
        
        # Step 7: Ensemble all solutions to select the best one
        solutions = [
            reasoning_step,
            structured_solution,
            count_solution,
            arithmetic_solution,
            comparison_solution,
            baseline_answer
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer