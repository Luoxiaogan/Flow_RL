# Workflow ID: drop_612_0
# Benchmark: drop
# Data Indices: [3412, 3813, 2891, 643]

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
        Uses step-by-step breakdowns, specialized operators, and ensemble selection.
        """
        # Step 1: Use Custom to extract key facts from the passage
        extraction = await self.custom(instruction="Break down the problem into smaller steps and identify all relevant numerical or categorical data.")

        # Step 2: Generate initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Use ComparisonReasoning if the task involves comparing values
        comparison_result = await self.comparison_reasoning()

        # Step 4: Use CountingReasoning if the task involves counting entities
        counting_result = await self.counting_reasoning()

        # Step 5: Use ArithmeticReasoning if the task involves numerical operations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: Ensemble multiple solutions (including original and specialized results)
        solutions = [
            initial_answer,
            comparison_result,
            counting_result,
            arithmetic_result,
            extraction
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 7: Final review to refine the best solution
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution