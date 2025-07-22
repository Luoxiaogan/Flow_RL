# Workflow ID: drop_7_0
# Benchmark: drop
# Data Indices: [3179, 3441, 1704, 3079]

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
        This is a comprehensive workflow graph for reading comprehension and discrete reasoning.
        It uses multiple specialized operators and ensembles their results for robustness.
        """
        # Step 1: Generate initial answer using direct reasoning
        solution1 = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        solution2 = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["extract_relevant_info", "identify_key_values", "perform_calculation_or_comparison", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        solution3 = await self.flexible_custom(
            custom_instruction="Carefully analyze and refine your answer through multiple iterations",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "check_for_errors", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Enforce comparison reasoning for problems involving max/min or relative differences
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        ensemble_solutions = [solution1, solution2, solution3, comparison_result]
        final_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_solution