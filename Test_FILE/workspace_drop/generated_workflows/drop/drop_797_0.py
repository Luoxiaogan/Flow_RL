# Workflow ID: drop_797_0
# Benchmark: drop
# Data Indices: [693, 2324, 1091, 2231, 3369]

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
        This is a workflow graph optimized for step-by-step reasoning.
        Uses specialized operators based on problem type and ensembles results.
        """
        # Step 1: Generate initial answer with full reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom to refine the solution using structured reasoning
        refined_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps, reason through each logically, and verify your final answer.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_result"]
        )

        # Step 3: If problem involves counting, use dedicated counting operator
        counting_result = await self.counting_reasoning()

        # Step 4: If problem involves arithmetic, use dedicated arithmetic operator
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If problem requires comparison, use dedicated comparison operator
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            refined_solution,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer