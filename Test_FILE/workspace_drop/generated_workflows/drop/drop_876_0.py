# Workflow ID: drop_876_0
# Benchmark: drop
# Data Indices: [3288, 255, 931, 2352]

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
        It uses specialized operators based on problem type and ensembles results.
        """
        # Step 1: Use flexible custom to extract key elements from the passage (sequential reasoning)
        extraction = await self.flexible_custom(
            custom_instruction="Break down the passage into key events, entities, and numerical facts.",
            reasoning_pattern="sequential",
            steps=["extract_events", "identify_entities", "locate_numbers"]
        )

        # Step 2: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Try counting-based reasoning if applicable
        count_result = await self.counting_reasoning()

        # Step 4: Try arithmetic reasoning if applicable
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Try comparison reasoning if applicable
        comparison_result = await self.comparison_reasoning()

        # Step 6: Review the direct answer for consistency
        reviewed_answer = await self.review(pre_solution=direct_answer)

        # Step 7: Ensemble all solutions to pick the best one
        solutions = [direct_answer, count_result, arithmetic_result, comparison_result, reviewed_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution