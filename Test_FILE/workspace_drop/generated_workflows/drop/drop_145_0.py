# Workflow ID: drop_145_0
# Benchmark: drop
# Data Indices: [1503, 2755, 2886, 1573, 2625]

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
        It uses specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use Custom to break down the problem into steps for better clarity
        reasoning_steps = await self.custom(instruction="Break down the problem into smaller steps and explain each step in detail.")

        # Step 3: Extract key numbers or values for arithmetic or counting tasks
        arithmetic_result = await self.arithmetic_reasoning()
        counting_result = await self.counting_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions from different reasoning paths
        solutions = [
            initial_answer,
            reasoning_steps,
            arithmetic_result,
            counting_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the final solution for consistency and correctness
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution