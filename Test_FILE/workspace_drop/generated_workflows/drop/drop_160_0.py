# Workflow ID: drop_160_0
# Benchmark: drop
# Data Indices: [3216, 3710, 1107, 2783]

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
        # Step 1: Extract key information with Custom (step-by-step thinking encouraged)
        extracted_info = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 2: Generate initial answer directly
        direct_answer = await self.answer_generate()

        # Step 3: Use flexible custom for structured reasoning based on problem type
        structured_reasoning = await self.flexible_custom(
            custom_instruction="Follow a sequential reasoning pattern to solve this problem carefully",
            reasoning_pattern="sequential",
            steps=["extract_key_facts", "identify_question_type", "apply_logical_reasoning", "verify_solution"]
        )

        # Step 4: Use specialized operators for numerical tasks (counting, arithmetic, comparison)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all generated solutions to select the best one
        solutions = [
            extracted_info,
            direct_answer,
            structured_reasoning,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        # Step 6: Optional review to refine the best solution
        refined_solution = await self.review(pre_solution=final_solution)

        return refined_solution