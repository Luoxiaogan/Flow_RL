# Workflow ID: drop_96_0
# Benchmark: drop
# Data Indices: [3952, 3413, 2186, 752]

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
        Uses step-by-step extraction, specialized reasoning, and ensemble selection.
        """
        # Step 1: Extract key information using Custom (step-by-step reasoning)
        extracted_info = await self.custom(instruction="Break down the passage into key events, scores, and entities relevant to the question. Think step by step.")

        # Step 2: Generate initial answer based on extracted info
        initial_answer = await self.answer_generate()

        # Step 3: Use specialized operators based on likely problem type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [
            initial_answer,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review of the ensembled solution
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer