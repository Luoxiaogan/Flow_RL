# Workflow ID: drop_420_0
# Benchmark: drop
# Data Indices: [2009, 1021, 3722, 567, 828]

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
        It uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Get base answer from direct generation
        base_answer = await self.answer_generate()

        # Step 2: Use flexible custom to explore multiple reasoning paths
        flexible_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps with clear reasoning",
            reasoning_pattern="sequential",
            steps=["identify_key_elements", "extract_numerical_data", "apply_logical_rules", "validate_result"]
        )

        # Step 3: If problem involves counting, use dedicated counting operator
        counting_result = await self.counting_reasoning()

        # Step 4: If problem involves arithmetic, use dedicated arithmetic operator
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If problem involves comparisons, use dedicated comparison operator
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions for final selection
        solutions = [base_answer, flexible_solution, counting_result, arithmetic_result, comparison_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer