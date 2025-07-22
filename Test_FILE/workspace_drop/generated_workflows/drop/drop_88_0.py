# Workflow ID: drop_88_0
# Benchmark: drop
# Data Indices: [1058, 3440, 3330, 585]

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
        It uses step-by-step reasoning with specialized operators and ensembles multiple solutions.
        """
        # Step 1: Generate initial answer using direct reasoning
        solution1 = await self.answer_generate()

        # Step 2: Use flexible custom to break down the problem logically
        solution2 = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and solve each one carefully",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_operation", "perform_calculation", "verify_solution"]
        )

        # Step 3: Use counting reasoning if applicable (e.g., counting events or items)
        solution3 = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning for numerical computations
        solution4 = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning for max/min or relative values
        solution5 = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to select the best one
        solutions = [solution1, solution2, solution3, solution4, solution5]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer