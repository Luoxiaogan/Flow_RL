# Workflow ID: drop_197_0
# Benchmark: drop
# Data Indices: [2952, 2784, 3445, 675, 1628]

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
        This is a workflow graph optimized for iterative improvement.
        Starts with direct answer generation, then refines using review.
        Ensemble of multiple reasoning paths ensures robustness.
        """
        # Step 1: Generate initial solution
        initial_solution = await self.answer_generate()

        # Step 2: Review to refine the initial solution
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Use flexible custom for structured step-by-step reasoning
        structured_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and reason through each one carefully.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_operation", "compute_step_by_step", "verify_final_answer"]
        )

        # Step 4: Ensembling all three solutions to get the best result
        solutions = [initial_solution, refined_solution, structured_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer