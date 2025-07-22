# Workflow ID: drop_107_0
# Benchmark: drop
# Data Indices: [3089, 1675, 2307, 302, 2136]

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
        Uses step-by-step breakdown, specialized operators, and ensemble to improve accuracy.
        """
        # Step 1: Extract key elements using Custom (reasoning-focused instruction)
        extracted = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Use specialized reasoning operators based on likely task type
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 3: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 4: Ensemble multiple solutions for robustness
        solutions = [extracted, counting_result, arithmetic_result, comparison_result, direct_answer]
        ensembled = await self.sc_ensemble(solutions=solutions)

        # Step 5: Review the ensembled solution for refinement
        final_solution = await self.review(pre_solution=ensembled)

        return final_solution