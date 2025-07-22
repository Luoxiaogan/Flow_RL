# Workflow ID: drop_47_0
# Benchmark: drop
# Data Indices: [3482, 1935, 3281, 3189, 3096]

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
        This is a robust workflow graph using Parallel Ensemble for enhanced accuracy.
        Generates multiple solutions via different reasoning paths, then ensembles the best.
        """
        # Step 1: Generate base answer directly
        base_answer = await self.answer_generate()

        # Step 2: Use Custom to break down the problem step-by-step
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use CountingReasoning for problems involving counts (e.g., field goals, touchdowns)
        counting_result = await self.counting_reasoning()

        # Step 4: Use ArithmeticReasoning for numerical totals (e.g., total yards)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use ComparisonReasoning for relative comparisons (e.g., which team scored more)
        comparison_result = await self.comparison_reasoning()

        # Step 6: Use FlexibleCustom with iterative refinement for complex discrete reasoning
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Carefully count or compute while iteratively verifying your result",
            reasoning_pattern="iterative",
            steps=["identify_values", "perform_calculation", "verify_result"],
            max_iterations=2
        )

        # Step 7: Ensemble all solutions to select the most consistent one
        solutions = [
            base_answer,
            step_by_step,
            counting_result,
            arithmetic_result,
            comparison_result,
            iterative_refinement
        ]
        
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution