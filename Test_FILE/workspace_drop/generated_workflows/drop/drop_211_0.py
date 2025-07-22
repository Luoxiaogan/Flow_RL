# Workflow ID: drop_211_0
# Benchmark: drop
# Data Indices: [1914, 3538, 1488, 1485]

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
        Uses specialized operators based on problem type, with ensemble and review for robustness.
        """
        # Step 1: Extract and reason step-by-step using flexible custom reasoning
        solution1 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logical_reasoning", "generate_answer"]
        )

        # Step 2: Use counting reasoning if applicable (e.g., count events, entities)
        solution2 = await self.counting_reasoning()

        # Step 3: Use arithmetic reasoning for numerical computations
        solution3 = await self.arithmetic_reasoning()

        # Step 4: Use comparison reasoning for max/min or relative comparisons
        solution4 = await self.comparison_reasoning()

        # Step 5: Generate direct answer as baseline
        solution5 = await self.answer_generate()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [solution1, solution2, solution3, solution4, solution5]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution