# Workflow ID: drop_298_0
# Benchmark: drop
# Data Indices: [760, 1527, 2065, 300, 3417]

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
        It uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Use Custom to extract and structure the problem logically
        structured_solution = await self.custom(instruction="Break down the problem into clear steps and explain each reasoning phase in detail.")

        # Step 2: Generate direct answer (for baseline)
        direct_answer = await self.answer_generate()

        # Step 3: Use specialized reasoning operators based on inferred task type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble all solutions to pick the best one
        solutions = [
            structured_solution,
            direct_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer