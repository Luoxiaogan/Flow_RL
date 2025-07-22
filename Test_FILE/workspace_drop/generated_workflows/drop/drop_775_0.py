# Workflow ID: drop_775_0
# Benchmark: drop
# Data Indices: [3650, 2619, 1841, 1080, 46]

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
        # Step 1: Get initial answer using direct generation
        solution_a = await self.answer_generate()

        # Step 2: Use custom reasoning to break down the problem into steps
        solution_b = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 3: Apply counting reasoning if needed (e.g., for "how many" questions)
        solution_c = await self.counting_reasoning()

        # Step 4: Apply arithmetic reasoning for numerical calculations
        solution_d = await self.arithmetic_reasoning()

        # Step 5: Apply comparison reasoning for max/min or ranking tasks
        solution_e = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [solution_a, solution_b, solution_c, solution_d, solution_e]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution