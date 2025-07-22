# Workflow ID: drop_143_0
# Benchmark: drop
# Data Indices: [1901, 1997, 2965, 549, 3787]

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
        Uses specialized operators based on problem type and ensembles results.
        """
        # Step 1: Extract and understand the problem via Custom reasoning
        initial_analysis = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Use specialized operators to compute relevant values
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 3: Generate direct answer as a baseline
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions for robustness
        solution_list = [
            initial_analysis,
            counting_result,
            arithmetic_result,
            comparison_result,
            direct_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 5: Optional review to refine the final output
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution