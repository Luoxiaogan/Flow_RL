# Workflow ID: drop_620_0
# Benchmark: drop
# Data Indices: [2109, 2935, 37, 1863, 481]

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
        This is a comprehensive reasoning workflow for reading comprehension and discrete reasoning.
        Uses multiple specialized operators and ensembles solutions for robustness.
        """
        # Step 1: Get base answer using direct generation
        base_answer = await self.answer_generate()

        # Step 2: Generate a detailed step-by-step solution using Custom
        detailed_step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom in sequential mode for structured reasoning
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Follow a clear sequence: extract relevant data, identify operations, compute, verify.",
            reasoning_pattern="sequential",
            steps=["extract_relevant_data", "identify_operation", "perform_calculation", "verify_result"]
        )

        # Step 4: Ensemple all three solutions to find the best one
        solutions = [base_answer, detailed_step_by_step, structured_reasoning]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution