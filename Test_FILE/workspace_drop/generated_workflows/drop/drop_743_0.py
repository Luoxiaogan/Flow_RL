# Workflow ID: drop_743_0
# Benchmark: drop
# Data Indices: [3479, 61, 930, 3174]

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
        This is a workflow graph optimized for step-by-step reasoning and ensemble-based solution selection.
        Uses specialized operators based on task type and ensures information flow from extraction to final answer.
        """
        # Step 1: Extract key elements using flexible custom with sequential reasoning
        extracted_info = await self.flexible_custom(
            custom_instruction="Break down the problem into key numerical or categorical elements step by step.",
            reasoning_pattern="sequential",
            steps=["extract_values", "identify_question_type", "classify_task"]
        )

        # Step 2: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 3: Use counting reasoning if applicable (e.g., "how many" questions)
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if computation needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if max/min or relative values are asked
        comparison_result = await self.comparison_reasoning()

        # Step 6: Review the direct answer for potential improvements
        reviewed_answer = await self.review(pre_solution=direct_answer)

        # Step 7: Ensemble all solutions to select the best one
        solutions = [
            direct_answer,
            counting_result,
            arithmetic_result,
            comparison_result,
            reviewed_answer,
            extracted_info
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer