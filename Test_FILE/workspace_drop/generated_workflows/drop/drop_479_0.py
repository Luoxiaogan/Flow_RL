# Workflow ID: drop_479_0
# Benchmark: drop
# Data Indices: [2115, 2036, 48, 2897]

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
        # Step 1: Use Custom to extract key elements from the passage in a structured way
        structured_analysis = await self.custom(instruction="Break down the passage into key events, numbers, and relationships relevant to the question. Be precise and step-by-step.")

        # Step 2: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 3: If the problem involves counting, use CountingReasoning
        count_result = await self.counting_reasoning()

        # Step 4: If the problem involves arithmetic operations, use ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If the problem requires comparison (e.g., max/min, differences), use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            count_result,
            arithmetic_result,
            comparison_result,
            structured_analysis
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution