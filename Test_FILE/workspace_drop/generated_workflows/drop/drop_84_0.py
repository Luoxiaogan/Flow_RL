# Workflow ID: drop_84_0
# Benchmark: drop
# Data Indices: [1555, 2799, 3763, 499, 76]

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
        This is a workflow graph optimized for reading comprehension and discrete reasoning.
        Uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Extract key information using flexible custom reasoning (sequential pattern)
        extraction = await self.flexible_custom(
            custom_instruction="Break down the passage into relevant facts step by step",
            reasoning_pattern="sequential",
            steps=["identify_key_events", "extract_numerical_data", "map_to_question"]
        )

        # Step 2: Use counting reasoning if the question involves counting
        counting_result = await self.counting_reasoning()

        # Step 3: Use arithmetic reasoning if numerical computation is needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use comparison reasoning if max/min or relative values are required
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate a direct answer as baseline
        direct_answer = await self.answer_generate()

        # Step 6: Review the direct answer to improve accuracy
        reviewed_answer = await self.review(pre_solution=direct_answer)

        # Step 7: Ensemble all solutions for final decision
        solutions = [
            extraction,
            counting_result,
            arithmetic_result,
            comparison_result,
            direct_answer,
            reviewed_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution