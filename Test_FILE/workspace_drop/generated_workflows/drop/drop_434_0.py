# Workflow ID: drop_434_0
# Benchmark: drop
# Data Indices: [3042, 2439, 3385, 1174, 3341]

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
        Uses specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Use Custom to extract key information from the passage in a structured way
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Run specialized reasoning operators based on problem type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions to improve accuracy
        solutions = [
            initial_answer,
            extracted_info,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensembled solution for refinement
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution