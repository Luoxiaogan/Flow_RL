# Workflow ID: drop_195_0
# Benchmark: drop
# Data Indices: [1451, 657, 2194, 3641]

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
        It uses specialized operators based on task type and ensembles multiple solutions for robustness.
        """
        # Step 1: Use Custom to extract key information from the passage
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and identify all relevant numerical or comparative data.")

        # Step 2: Generate initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Use CountingReasoning for counting tasks (if needed)
        count_result = await self.counting_reasoning()

        # Step 4: Use ArithmeticReasoning for calculations (if needed)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use ComparisonReasoning for max/min or ranking tasks (if needed)
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble multiple solutions to improve accuracy
        solution_list = [initial_answer, count_result, arithmetic_result, comparison_result]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 7: Final review to refine the best solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer