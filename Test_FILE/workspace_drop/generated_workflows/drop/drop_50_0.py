# Workflow ID: drop_50_0
# Benchmark: drop
# Data Indices: [3636, 1610, 604, 2841, 1942]

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
        Uses step-by-step breakdowns, specialized operators, and ensemble to improve accuracy.
        """
        # Step 1: Break down the problem with Custom to encourage structured thinking
        step_by_step_analysis = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Use Counting/Arithmetic/Comparison Reasoning based on task type (no conditionals — let operators decide internally)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [
            step_by_step_analysis,
            initial_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review of the best solution to refine any remaining issues
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer