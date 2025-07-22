# Workflow ID: drop_67_0
# Benchmark: drop
# Data Indices: [2700, 3249, 1622, 2086, 3627]

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
        Uses specialized operators based on problem type and ensembles multiple solutions for robustness.
        """
        # Step 1: Use Custom to break down the problem into smaller steps with clear reasoning
        structured_plan = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Use CountingReasoning if the problem involves counting (e.g., touchdowns, households, etc.)
        counting_result = await self.counting_reasoning()

        # Step 4: Use ArithmeticReasoning for numerical computations (e.g., total yards, percentages, etc.)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use ComparisonReasoning for max/min or relative comparisons (e.g., who scored more?)
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all generated solutions to select the best one
        solutions = [structured_plan, direct_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution