# Workflow ID: drop_15_0
# Benchmark: drop
# Data Indices: [3889, 163, 2995, 3755]

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
        This is a workflow graph optimized for step-by-step reasoning in reading comprehension and discrete reasoning.
        It uses specialized operators based on problem type and ensembles multiple solutions for robustness.
        """
        # Step 1: Use Custom to break down the problem into smaller steps with clear reasoning
        structured_plan = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Use CountingReasoning if the problem involves counting entities or events
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if the problem involves numerical calculations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning if the problem requires finding max/min or comparing values
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate a direct answer using AnswerGenerate as baseline
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble all results to select the best solution
        solutions = [
            structured_plan,
            count_result,
            arithmetic_result,
            comparison_result,
            direct_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution