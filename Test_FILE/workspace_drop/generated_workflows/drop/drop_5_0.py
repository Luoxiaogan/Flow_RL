# Workflow ID: drop_5_0
# Benchmark: drop
# Data Indices: [2175, 1647, 2094, 1931, 2939]

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
        This is a robust workflow graph using Parallel Ensemble pattern.
        Generates multiple solutions via different reasoning strategies, then ensembles them.
        """
        # Step 1: Generate base answer directly
        base_answer = await self.answer_generate()

        # Step 2: Generate step-by-step breakdown using Custom
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use flexible custom with sequential reasoning for structured logic
        sequential_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using logical deduction.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_reasoning_logic", "generate_answer"]
        )

        # Step 4: Use flexible custom with iterative refinement (for accuracy)
        iterative_solution = await self.flexible_custom(
            custom_instruction="Refine your answer through careful iteration to avoid errors.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "verify_consistency", "refine_final_answer"],
            max_iterations=2
        )

        # Step 5: Use ComparisonReasoning if the problem involves comparisons
        comparison_result = await self.comparison_reasoning()

        # Step 6: Use CountingReasoning if the problem involves counting entities
        counting_result = await self.counting_reasoning()

        # Step 7: Use ArithmeticReasoning if the problem involves calculations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 8: Ensembling all solutions using ScEnsemble
        solutions = [
            base_answer,
            step_by_step,
            sequential_solution,
            iterative_solution,
            comparison_result,
            counting_result,
            arithmetic_result
        ]

        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer