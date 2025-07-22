# Workflow ID: drop_589_0
# Benchmark: drop
# Data Indices: [1787, 3283, 2353, 1749, 1634]

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
        Uses step-by-step breakdown, specialized reasoning operators, and ensemble selection.
        """
        # Step 1: Break down the problem logically with Custom reasoning
        reasoning_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Use CountingReasoning if counting is needed (e.g., field goals < 25 yards)
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if numerical computation is required (e.g., yard differences)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning for max/min or comparisons (e.g., more yards between players)
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate final answer directly from problem
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble multiple solutions to improve robustness
        solutions = [reasoning_step, count_result, arithmetic_result, comparison_result, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution