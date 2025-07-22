# Workflow ID: drop_652_0
# Benchmark: drop
# Data Indices: [2691, 3837, 2394, 837, 3234]

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
        It uses specialized operators based on problem type and ensembles results for robustness.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use Custom to break down the problem into steps for clarity
        step_by_step_analysis = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Step 3: Perform counting if needed (e.g., number of events, entities)
        counting_result = await self.counting_reasoning()

        # Step 4: Perform arithmetic if needed (e.g., calculations, percentages)
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Perform comparison if needed (e.g., max/min, relative values)
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble multiple solutions for better accuracy
        solutions = [initial_answer, step_by_step_analysis, counting_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 7: Review the final solution for refinement
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution