# Workflow ID: drop_301_0
# Benchmark: drop
# Data Indices: [175, 3213, 911, 2550]

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
        Starts with direct answer generation, then refines via review.
        Uses ensemble to select the best solution from multiple approaches.
        """
        # Step 1: Generate initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to improve it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Generate alternative reasoning paths using flexible custom (iterative refinement)
        iterative_answer = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and refine your answer iteratively",
            reasoning_pattern="iterative",
            steps=["understand_problem", "extract_key_info", "reason_step_by_step", "verify_final_answer"],
            max_iterations=2
        )

        # Step 4: Ensemble all solutions to get the best one
        solutions = [initial_answer, refined_answer, iterative_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution