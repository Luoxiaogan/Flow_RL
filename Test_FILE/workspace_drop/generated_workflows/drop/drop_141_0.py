# Workflow ID: drop_141_0
# Benchmark: drop
# Data Indices: [3167, 2073, 3111, 2040, 3425]

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
        and finally ensembles multiple reasoning approaches to ensure robustness.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial solution for refinement
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom for structured reasoning (sequential pattern)
        structured_answer = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step with clear reasoning for each step",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_criteria", "evaluate_candidates", "verify_result"]
        )

        # Step 4: Ensemble all three solutions for final selection
        solutions = [initial_answer, refined_answer, structured_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer