# Workflow ID: drop_45_0
# Benchmark: drop
# Data Indices: [3849, 2425, 1632, 776]

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
        Uses step-by-step extraction, specialized reasoning, and ensemble to improve accuracy.
        """
        # Step 1: Extract key information from the passage using Custom
        extracted_info = await self.custom(instruction="Break down the passage into key events and numerical data relevant to the question. Be precise and structured.")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Use CountingReasoning for problems requiring counting (e.g., field goals, touchdowns)
        counting_result = await self.counting_reasoning()

        # Step 4: Use ArithmeticReasoning for numerical comparisons or calculations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use ComparisonReasoning for max/min or comparative questions
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble multiple solutions to select the best one
        solutions = [initial_answer, counting_result, arithmetic_result, comparison_result]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 7: Final review to refine the selected solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer