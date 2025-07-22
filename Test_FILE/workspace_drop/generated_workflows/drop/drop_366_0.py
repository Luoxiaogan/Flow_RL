# Workflow ID: drop_366_0
# Benchmark: drop
# Data Indices: [2339, 1762, 3513, 3557, 3971]

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
        Starts with direct answer generation, then refines via review,
        and finally ensembles multiple reasoning approaches for robustness.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to improve accuracy
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom for structured step-by-step reasoning
        structured_answer = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps with logical reasoning",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_result"]
        )

        # Step 4: Ensembling multiple solutions (including original, reviewed, and structured)
        solutions = [initial_answer, refined_answer, structured_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer