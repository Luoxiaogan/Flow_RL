# Workflow ID: drop_707_0
# Benchmark: drop
# Data Indices: [865, 609, 3498, 3218, 1014]

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
        Uses specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Generate initial answer using direct reasoning
        solution1 = await self.answer_generate()

        # Step 2: Use custom reasoning to break down the problem into steps
        solution2 = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 3: Use counting reasoning if applicable (e.g., "how many", "count")
        solution3 = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning if numerical computation needed
        solution4 = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if max/min or comparison is required
        solution5 = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [solution1, solution2, solution3, solution4, solution5]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution