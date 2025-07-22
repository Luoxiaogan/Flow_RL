# Workflow ID: drop_191_0
# Benchmark: drop
# Data Indices: [164, 2102, 687, 3221]

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
        It uses specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Use Custom to extract key elements from the passage step-by-step
        extraction = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: Run counting reasoning if the problem involves counting (e.g., field goals, yards)
        counting_result = await self.counting_reasoning()

        # Step 4: Run arithmetic reasoning if the problem involves numerical computation (e.g., total yards)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Run comparison reasoning if the problem requires max/min or sorting (e.g., longest field goal)
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all results to select the best solution
        solutions = [initial_answer, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution