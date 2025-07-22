# Workflow ID: drop_426_0
# Benchmark: drop
# Data Indices: [2296, 2752, 3824, 184, 3812]

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
        # Step 1: Use Custom to break down the problem into smaller steps with clear reasoning
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 2: Generate a direct answer (this may be used as one of the ensemble candidates)
        direct_answer = await self.answer_generate()

        # Step 3: Use ComparisonReasoning if the problem involves comparisons (e.g., "which happened later")
        comparison_result = await self.comparison_reasoning()

        # Step 4: Use ArithmeticReasoning if numerical computation is needed (e.g., "how many yards longer")
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use CountingReasoning if the task involves counting entities or events
        counting_result = await self.counting_reasoning()

        # Step 6: Ensemble all results to select the best solution
        solutions = [step_by_step, direct_answer, comparison_result, arithmetic_result, counting_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer