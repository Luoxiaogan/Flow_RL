# Workflow ID: drop_549_0
# Benchmark: drop
# Data Indices: [2410, 3578, 1873, 2538]

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
        It uses step-by-step reasoning with specialized operators based on task type.
        """
        # Step 1: Use Custom to break down the problem into smaller steps
        reasoning_steps = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Use CountingReasoning if the problem involves counting entities or events
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if numerical computation is needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning if max/min or comparison is required
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 6: Review the initial answer for correctness and clarity
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 7: Ensemble multiple solutions (including custom reasoning, counts, arithmetic, comparisons, and reviews)
        solutions = [
            reasoning_steps,
            count_result,
            arithmetic_result,
            comparison_result,
            initial_answer,
            reviewed_answer
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer