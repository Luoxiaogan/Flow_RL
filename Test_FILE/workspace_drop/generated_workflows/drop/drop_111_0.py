# Workflow ID: drop_111_0
# Benchmark: drop
# Data Indices: [2165, 1619, 422, 3690]

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
        It uses specialized operators based on problem type and ensembles multiple solutions for robustness.
        """
        # Step 1: Use Custom to extract key elements from the passage in a structured way
        extraction = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate an initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 3: Use CountingReasoning if the question involves counting entities/events
        counting_result = await self.counting_reasoning()

        # Step 4: Use ArithmeticReasoning if the question involves numerical computation
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use ComparisonReasoning if the question involves comparing values or entities
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all generated solutions to select the best one
        solutions = [direct_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution