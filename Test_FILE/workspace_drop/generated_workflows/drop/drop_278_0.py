# Workflow ID: drop_278_0
# Benchmark: drop
# Data Indices: [2121, 145, 2750, 2633]

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
        It uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Use Custom to extract key elements from the passage
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Run specialized reasoning operators depending on problem type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [initial_answer, counting_result, arithmetic_result, comparison_result]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensembled solution for refinement
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer