# Workflow ID: drop_116_0
# Benchmark: drop
# Data Indices: [2844, 682, 2753, 2519, 1519]

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
        It uses specialized operators based on task type and ensembles multiple solutions to improve accuracy.
        """
        # Step 1: Use Custom to extract and reason step-by-step from the passage
        reasoning_step = await self.custom(instruction="Can you break down the problem into smaller steps and explain the reasoning behind each step?")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Run specialized reasoning operators based on likely task types
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble all results to select the best solution
        solutions = [initial_answer, reasoning_step, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensemble result to refine it further
        reviewed_solution = await self.review(pre_solution=final_solution)

        return reviewed_solution