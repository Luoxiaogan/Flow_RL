# Workflow ID: drop_11_0
# Benchmark: drop
# Data Indices: [1253, 1554, 1616, 3707]

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
        This is a workflow graph optimized for efficiency and correctness.
        It selects the appropriate specialized operator based on problem type.
        """
        # Step 1: Use Custom to break down the problem into steps
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Determine problem type and apply specialized reasoning
        if "count" in step_by_step.lower() or "how many" in step_by_step.lower():
            count_result = await self.counting_reasoning()
            return count_result
        elif "percent" in step_by_step.lower() or "percentage" in step_by_step.lower():
            arithmetic_result = await self.arithmetic_reasoning()
            return arithmetic_result
        elif "more" in step_by_step.lower() or "less" in step_by_step.lower() or "compare" in step_by_step.lower():
            comparison_result = await self.comparison_reasoning()
            return comparison_result
        else:
            # Default fallback: use answer generation
            final_answer = await self.answer_generate()
            return final_answer