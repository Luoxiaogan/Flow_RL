# Workflow ID: drop_12_0
# Benchmark: drop
# Data Indices: [159, 273, 18, 337, 2043]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.agent = create(config)
        self.custom = operator.Custom(self.agent, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.agent, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.agent, self.problem)
        self.review = operator.Review(self.agent, self.problem)
        self.counting_reasoning = operator.CountingReasoning(self.agent, self.problem)
        self.arithmetic_reasoning = operator.ArithmeticReasoning(self.agent, self.problem)
        self.comparison_reasoning = operator.ComparisonReasoning(self.agent, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.agent, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph optimized for iterative improvement.
        Starts with direct answer generation, then refines using review.
        For complex problems, uses flexible custom reasoning to ensure structured thinking.
        """
        # Step 1: Generate initial solution
        initial_solution = await self.answer_generate()

        # Step 2: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Use flexible custom reasoning for complex problems (e.g., counting, arithmetic, comparison)
        # This step ensures structured and robust reasoning by leveraging iterative or sequential patterns
        reasoning_pattern = "iterative" if "count" in self.problem.lower() or "how many" in self.problem.lower() else "sequential"
        flexible_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and reason carefully",
            reasoning_pattern=reasoning_pattern,
            steps=["understand_question", "extract_relevant_info", "perform_calculation_or_comparison", "verify_result"]
        )

        # Step 4: Ensemble the refined solution and the flexible solution to improve accuracy
        ensemble_solution = await self.sc_ensemble(solutions=[refined_solution, flexible_solution])

        return ensemble_solution