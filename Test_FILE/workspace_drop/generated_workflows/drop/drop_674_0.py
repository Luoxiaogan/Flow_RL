# Workflow ID: drop_674_0
# Benchmark: drop
# Data Indices: [3269, 3135, 1651, 2120, 3146]

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
        Uses step-by-step reasoning via Custom + specialized operators (Counting, Arithmetic, Comparison),
        with ensemble and review for robustness.
        """
        # Step 1: Use Custom to break down the problem into logical steps
        reasoning_steps = await self.custom(instruction="Break down the problem into clear, logical steps and explain each one in detail.")

        # Step 2: Apply specialized reasoning based on task type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 3: Generate an answer directly using the problem context
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions to improve accuracy
        solutions = [reasoning_steps, counting_result, arithmetic_result, comparison_result, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the final solution for clarity and correctness
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution