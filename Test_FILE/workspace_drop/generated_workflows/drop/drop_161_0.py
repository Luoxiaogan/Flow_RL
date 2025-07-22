# Workflow ID: drop_161_0
# Benchmark: drop
# Data Indices: [2364, 3430, 2488, 2532, 53]

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
        Uses specialized operators based on problem type, with ensemble and review to improve accuracy.
        """
        # Step 1: Extract key information using Custom (reasoning-focused instruction)
        extracted_info = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 2: Generate initial answer directly from problem
        direct_answer = await self.answer_generate()

        # Step 3: Use specialized reasoning operators depending on task type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for robustness
        solution_list = [
            extracted_info,
            direct_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 5: Review the ensembled solution to refine it
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer