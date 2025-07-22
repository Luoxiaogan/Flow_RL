class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
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
        This is a robust workflow graph using Parallel Ensemble for enhanced accuracy.
        It generates multiple reasoning paths and selects the best solution via ensemble.
        """
        # Step 1: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 2: Use custom reasoning to break down the problem step-by-step
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use flexible custom with sequential pattern for structured reasoning
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Solve this problem using a step-by-step approach with clear logic",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_solution"]
        )

        # Step 4: If the problem involves counting, use dedicated counting reasoning
        if "count" in self.problem.lower() or "how many" in self.problem.lower():
            count_result = await self.counting_reasoning()
        else:
            count_result = ""

        # Step 5: If arithmetic is needed, perform it
        if any(op in self.problem.lower() for op in ["add", "subtract", "multiply", "divide", "percent", "percentage"]):
            arithmetic_result = await self.arithmetic_reasoning()
        else:
            arithmetic_result = ""

        # Step 6: If comparison is required, compare values
        if any(comp in self.problem.lower() for comp in ["larger", "smaller", "more", "less", "compare"]):
            comparison_result = await self.comparison_reasoning()
        else:
            comparison_result = ""

        # Step 7: Collect all solutions for parallel ensemble
        solutions = [
            direct_answer,
            step_by_step,
            structured_reasoning,
            count_result,
            arithmetic_result,
            comparison_result
        ]

        # Step 8: Enforce consistency across multiple approaches
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer