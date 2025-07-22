# Workflow ID: drop_368_0
# Benchmark: drop
# Data Indices: [1849, 3372, 2072, 2171]

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
        It uses step-by-step reasoning with specialized operators and ensembles multiple solutions.
        """
        # Step 1: Extract key information using Custom (step-by-step thinking)
        extraction = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate direct answer as baseline
        direct_answer = await self.answer_generate()

        # Step 3: Use counting reasoning if applicable (e.g., count touchdowns, events)
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if numerical computation needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if max/min or comparisons are required
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all results to select best solution
        solutions = [extraction, direct_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution