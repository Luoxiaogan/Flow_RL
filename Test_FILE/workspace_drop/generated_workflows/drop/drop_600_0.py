# Workflow ID: drop_600_0
# Benchmark: drop
# Data Indices: [1602, 2001, 2020, 3252]

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
        This is a comprehensive reasoning workflow using multiple specialized operators and ensemble.
        """
        # Step 1: Generate an initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        seq_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_information", "analyze_data", "formulate_answer"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iter_refinement = await self.flexible_custom(
            custom_instruction="Carefully count or compute, then verify your result to ensure completeness and correctness.",
            reasoning_pattern="iterative",
            steps=["initial_solution", "verify_accuracy", "refine_if_needed"],
            max_iterations=2
        )

        # Step 4: Use comparison reasoning if the problem involves comparing values
        comparison_result = await self.comparison_reasoning()

        # Step 5: Use counting reasoning if the problem involves counting entities
        counting_result = await self.counting_reasoning()

        # Step 6: Use arithmetic reasoning if the problem requires numerical computation
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 7: Ensemble all solutions to select the best one
        solutions = [
            direct_answer,
            seq_reasoning,
            iter_refinement,
            comparison_result,
            counting_result,
            arithmetic_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution