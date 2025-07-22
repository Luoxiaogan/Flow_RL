# Workflow ID: drop_359_0
# Benchmark: drop
# Data Indices: [670, 2407, 1082, 2368]

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
        Uses step-by-step reasoning via specialized operators and ensembles for robustness.
        """
        # Step 1: Extract key information using Custom reasoning
        extraction = await self.custom(instruction="Break down the problem into smaller steps and identify what needs to be calculated or compared.")

        # Step 2: Use specialized reasoning based on task type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 3: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions from different reasoning paths
        solutions = [
            extraction,
            counting_result,
            arithmetic_result,
            comparison_result,
            initial_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensemble result to improve accuracy
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution