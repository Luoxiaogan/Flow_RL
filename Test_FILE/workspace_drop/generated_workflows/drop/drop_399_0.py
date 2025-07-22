# Workflow ID: drop_399_0
# Benchmark: drop
# Data Indices: [3969, 1754, 3401, 1611]

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
        Starts with a direct answer, then refines it through review,
        and finally ensembles multiple reasoning approaches to ensure robustness.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer for refinement
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom for structured reasoning (sequential pattern)
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step with clear reasoning",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_evidence", "reason_step_by_step", "verify_conclusion"]
        )

        # Step 4: Generate one more solution using a custom instruction focused on step-by-step thinking
        detailed_step_by_step = await self.custom(
            instruction="Solve this by breaking it into clear, logical steps and explaining each reasoning phase."
        )

        # Step 5: Ensemble all solutions to select the best one
        solutions = [initial_answer, refined_answer, structured_reasoning, detailed_step_by_step]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer