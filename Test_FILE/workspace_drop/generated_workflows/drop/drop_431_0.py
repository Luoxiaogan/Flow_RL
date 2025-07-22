# Workflow ID: drop_431_0
# Benchmark: drop
# Data Indices: [1331, 1477, 3994, 803, 2403]

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
        Uses specialized operators based on problem type and ensembles results when needed.
        """
        # Step 1: Use Custom to guide structured reasoning
        guided_reasoning = await self.custom(instruction="Break down the problem into smaller steps and explain each reasoning step clearly.")

        # Step 2: Generate an initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()

        # Step 3: If the problem involves counting, use CountingReasoning for verification
        count_result = await self.counting_reasoning()

        # Step 4: If arithmetic is involved, compute it separately
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If comparison is needed (e.g., max/min), get that result
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [guided_reasoning, initial_answer, count_result, arithmetic_result, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution