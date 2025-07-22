# Workflow ID: drop_360_0
# Benchmark: drop
# Data Indices: [840, 1147, 97, 3435, 1515]

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
        This is a robust workflow graph using Parallel Ensemble pattern.
        Generates multiple solutions via different reasoning approaches, then selects the best one.
        """
        # Step 1: Generate base answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use custom reasoning to break down the problem step-by-step
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use specialized operators based on likely task types (no conditionals!)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Use flexible custom for structured reasoning (sequential pattern)
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Solve this problem with a clear sequence of reasoning steps",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_relevant_info", "apply_logic", "verify_solution"]
        )

        # Step 5: Create solution list for ensemble
        solutions = [
            direct_answer,
            step_by_step,
            counting_result,
            arithmetic_result,
            comparison_result,
            structured_reasoning
        ]

        # Step 6: Use ScEnsemble to select the most consistent and accurate answer
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer