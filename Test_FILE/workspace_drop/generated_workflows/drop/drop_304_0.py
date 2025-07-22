# Workflow ID: drop_304_0
# Benchmark: drop
# Data Indices: [986, 3351, 1557, 3972]

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
        Uses step-by-step reasoning with specialized operators based on task type.
        """
        # Step 1: Use Custom to break down the problem into clear steps
        structured_plan = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Use CountingReasoning if the problem involves counting entities or events
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning if numerical computation is required
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning if max/min or comparison is needed
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate direct answer using AnswerGenerate
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble multiple solutions to improve robustness
        solution_list = [structured_plan, count_result, arithmetic_result, comparison_result, direct_answer]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 7: Final review to refine the ensembled result
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer