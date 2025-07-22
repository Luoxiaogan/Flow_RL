# Workflow ID: drop_403_0
# Benchmark: drop
# Data Indices: [2503, 2159, 1035, 2151]

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
        Uses multiple operators in parallel and sequential patterns to enhance accuracy.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for step-by-step verification
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and explain each reasoning step",
            reasoning_pattern="sequential",
            steps=["identify_key_elements", "extract_values", "perform_calculation", "verify_result"]
        )

        # Step 3: Use flexible custom with iterative pattern for refinement
        iter_solution = await self.flexible_custom(
            custom_instruction="Carefully count or compute, then double-check for errors",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "validate_steps", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Use specialized operators for domain-specific tasks
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            seq_solution,
            iter_solution,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 6: Review the final solution for consistency and clarity
        reviewed_answer = await self.review(pre_solution=final_answer)

        return reviewed_answer