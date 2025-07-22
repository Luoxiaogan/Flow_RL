# Workflow ID: drop_464_0
# Benchmark: drop
# Data Indices: [1489, 3635, 891, 3962, 2942]

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
        This is a workflow graph optimized for step-by-step reasoning.
        It uses specialized operators based on problem type and ensembles results.
        """
        # Step 1: Use Custom to extract key information from the problem (step-by-step)
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Use CountingReasoning for counting-based problems
        count_result = await self.counting_reasoning()

        # Step 3: Use ArithmeticReasoning for numerical calculations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 4: Use ComparisonReasoning for comparison tasks
        comparison_result = await self.comparison_reasoning()

        # Step 5: Generate a direct answer using AnswerGenerate
        direct_answer = await self.answer_generate()

        # Step 6: Ensemble all solutions to pick the best one
        solutions = [extracted_info, count_result, arithmetic_result, comparison_result, direct_answer]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution