# Workflow ID: drop_287_0
# Benchmark: drop
# Data Indices: [1900, 2158, 1707, 233]

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
        It leverages specialized operators based on problem type and uses ensemble to improve accuracy.
        """
        # Step 1: Use Custom to extract key information step-by-step
        extraction = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")

        # Step 2: Run specialized reasoning based on task type (counting, arithmetic, comparison)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 3: Generate direct answer as baseline
        baseline_answer = await self.answer_generate()

        # Step 4: Ensemble all results to select best solution
        solutions = [
            extraction,
            counting_result,
            arithmetic_result,
            comparison_result,
            baseline_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution