# Workflow ID: drop_777_0
# Benchmark: drop
# Data Indices: [3535, 824, 3937, 3409]

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
        This is a workflow graph optimized for iterative improvement and ensemble refinement.
        Starts with direct answer generation, then refines via review, and finally uses ensemble to select the best solution.
        """
        # Step 1: Generate an initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to refine it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom reasoning for structured step-by-step verification (iterative pattern)
        structured_refinement = await self.flexible_custom(
            custom_instruction="Break down the problem into logical steps and verify each one carefully",
            reasoning_pattern="iterative",
            steps=["understand_problem", "identify_key_data", "apply_logic", "verify_result"],
            max_iterations=2
        )

        # Step 4: Ensemble multiple solutions to pick the best one
        solutions = [initial_answer, refined_answer, structured_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer