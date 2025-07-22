# Workflow ID: drop_627_0
# Benchmark: drop
# Data Indices: [1943, 3911, 937, 729, 2218]

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
        This is a workflow graph optimized for step-by-step reasoning in reading comprehension and discrete tasks.
        Uses specialized operators based on task type, with ensemble and review for robustness.
        """
        # Step 1: Use Custom to break down the problem into smaller steps
        structured_plan = await self.custom(instruction="Break down the problem into clear, logical steps. Explain each step before proceeding.")

        # Step 2: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 3: Extract key numerical data or entities for counting/arithmetic/comparison
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble multiple solutions (including original and specialized results)
        solution_list = [
            initial_answer,
            counting_result,
            arithmetic_result,
            comparison_result,
            structured_plan
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 5: Review the ensembled solution to refine accuracy
        final_solution = await self.review(pre_solution=ensembled_solution)

        return final_solution