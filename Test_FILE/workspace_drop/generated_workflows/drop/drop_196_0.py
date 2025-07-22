# Workflow ID: drop_196_0
# Benchmark: drop
# Data Indices: [3464, 1423, 3388, 1986]

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
        This is a comprehensive reasoning workflow that uses multiple specialized operators
        and ensembles their results to improve accuracy for reading comprehension and discrete reasoning.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        step_by_step_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step in detail.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_evidence", "reason_step_by_step", "verify_conclusion"]
        )

        # Step 3: Use flexible custom with iterative refinement for precision
        refined_answer = await self.flexible_custom(
            custom_instruction="Carefully count or compute the required value, then double-check your result.",
            reasoning_pattern="iterative",
            steps=["initial_calculation", "verify_accuracy", "refine_if_needed"],
            max_iterations=2
        )

        # Step 4: Generate an alternative solution using comparison reasoning (if applicable)
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            step_by_step_solution,
            refined_answer,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution