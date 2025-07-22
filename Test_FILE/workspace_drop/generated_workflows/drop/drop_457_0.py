# Workflow ID: drop_457_0
# Benchmark: drop
# Data Indices: [1351, 1134, 2608, 507, 47]

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
        It uses specialized operators based on task type and ensembles multiple solutions.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use Custom to extract key elements step-by-step (for structured thinking)
        extraction = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 3: Run counting reasoning if needed (e.g., for "how many" questions)
        counting_result = await self.counting_reasoning()

        # Step 4: Run arithmetic reasoning if needed (e.g., for score totals or yardage)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Run comparison reasoning if needed (e.g., for max/min differences)
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all generated solutions to pick the best one
        solutions = [
            initial_answer,
            extraction,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution