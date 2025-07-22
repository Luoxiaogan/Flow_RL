# Workflow ID: drop_144_0
# Benchmark: drop
# Data Indices: [1653, 1251, 248, 616, 3603]

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
        This is a workflow graph optimized for comprehensive reasoning.
        Uses multiple operators in sequence and ensemble to ensure robustness.
        """
        # Step 1: Generate an initial answer using direct reasoning
        solution1 = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for structured step-by-step breakdown
        solution2 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly",
            reasoning_pattern="sequential",
            steps=["identify_key_elements", "extract_numerical_data", "apply_logical_operations", "verify_consistency"]
        )

        # Step 3: Use counting reasoning if the problem involves enumeration
        solution3 = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if numerical computation is required
        solution4 = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if max/min or comparative logic is needed
        solution5 = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [solution1, solution2, solution3, solution4, solution5]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution