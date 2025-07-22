# Workflow ID: drop_3_0
# Benchmark: drop
# Data Indices: [645, 2818, 1735, 1852]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.agent = create(config)
        self.custom = operator.Custom(self.agent, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.agent, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.agent, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.agent, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.agent, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.agent, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph using Parallel Ensemble for robustness.
        Generates multiple solutions via different reasoning paths, then selects the best one.
        """
        # Step 1: Generate base answer directly
        base_answer = await self.answer_generate()

        # Step 2: Generate solution using step-by-step breakdown (Custom)
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use Counting Reasoning if applicable (e.g., counting touchdowns, field goals)
        counting_result = await self.counting_reasoning()

        # Step 4: Use Arithmetic Reasoning if numerical computation needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use Comparison Reasoning if comparing values or ranks
        comparison_result = await self.comparison_reasoning()

        # Step 6: Use Flexible Custom with sequential pattern to ensure structured reasoning
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Follow a structured approach: extract relevant info, identify key elements, reason step-by-step, verify logic",
            reasoning_pattern="sequential",
            steps=["extract_values", "identify_operation", "perform_calculation", "verify_result"]
        )

        # Step 7: Ensemble all generated solutions
        solutions = [
            base_answer,
            step_by_step,
            counting_result,
            arithmetic_result,
            comparison_result,
            structured_reasoning
        ]

        # Step 8: Select the most consistent answer using ScEnsemble
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer