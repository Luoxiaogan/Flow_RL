# Workflow ID: drop_477_0
# Benchmark: drop
# Data Indices: [2808, 698, 3984, 1181]

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
        Uses step-by-step reasoning with specialized operators and ensemble to improve accuracy.
        """
        # Step 1: Extract key information using Custom (step-by-step breakdown)
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 3: Use specialized reasoning based on task type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [extracted_info, direct_answer, counting_result, arithmetic_result, comparison_result]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review of the best solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer