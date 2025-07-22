# Workflow ID: drop_786_0
# Benchmark: drop
# Data Indices: [3832, 3878, 3137, 2228, 772]

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
        It uses step-by-step reasoning via specialized operators and ensembles multiple solutions.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use Custom to extract and break down the problem into steps
        reasoning_steps = await self.custom(instruction="Break down the problem into clear, logical steps with detailed reasoning for each.")

        # Step 3: Run specialized reasoning based on problem type (automatically handled by operators)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [
            initial_answer,
            reasoning_steps,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensemble result for refinement
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution