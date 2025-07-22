# Workflow ID: drop_328_0
# Benchmark: drop
# Data Indices: [1593, 243, 3691, 81]

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
        Uses specialized operators based on task type and ensembles results for robustness.
        """
        # Step 1: Extract relevant information using Custom (step-by-step breakdown)
        extraction = await self.custom(instruction="Break down the passage step by step to identify all numerical values related to the question.")

        # Step 2: Use CountingReasoning if the problem involves counting entities/events
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if the problem requires computation (e.g., total yards, points)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning if the problem asks for max/min or comparison
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate final answer directly from the problem
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble multiple solutions for higher accuracy
        solution_list = [extraction, count_result, arithmetic_result, comparison_result, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        return final_solution