# Workflow ID: drop_248_0
# Benchmark: drop
# Data Indices: [984, 1354, 1711, 2757, 3343]

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
        Ensembles multiple reasoning approaches for robustness.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to refine it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom for structured step-by-step reasoning (iterative refinement)
        structured_answer = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and reason through each one carefully.",
            reasoning_pattern="iterative",
            steps=["understand_question", "extract_evidence", "reason_step_by_step", "verify_consistency"],
            max_iterations=2
        )

        # Step 4: Ensemble all three solutions for final decision
        solutions = [initial_answer, refined_answer, structured_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer