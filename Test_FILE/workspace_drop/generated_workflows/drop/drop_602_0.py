# Workflow ID: drop_602_0
# Benchmark: drop
# Data Indices: [125, 2048, 2156, 3323, 3336]

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
        Generates multiple reasoning paths and selects the best answer via ensemble.
        """
        # Generate base solution using direct answer generation
        base_solution = await self.answer_generate()

        # Generate step-by-step reasoning solution
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Generate arithmetic-focused solution (if applicable)
        arithmetic_solution = await self.arithmetic_reasoning()

        # Generate counting-focused solution (if applicable)
        counting_solution = await self.counting_reasoning()

        # Generate comparison-focused solution (if applicable)
        comparison_solution = await self.comparison_reasoning()

        # Create a list of diverse solutions for ensemble
        solutions = [
            base_solution,
            step_by_step,
            arithmetic_solution,
            counting_solution,
            comparison_solution
        ]

        # Use ScEnsemble to select the most consistent and accurate solution
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer