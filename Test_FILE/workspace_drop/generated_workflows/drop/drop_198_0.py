# Workflow ID: drop_198_0
# Benchmark: drop
# Data Indices: [3164, 2692, 258, 2459]

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
        This is a workflow graph optimized for iterative improvement.
        Starts with direct answer generation, then refines via review.
        Uses ensemble to select best solution from multiple reasoning paths.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer for refinement
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom to perform step-by-step reasoning (sequential pattern)
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and explain each reasoning step thoroughly.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_relevant_info", "apply_logic", "verify_solution"]
        )

        # Step 4: Use arithmetic reasoning if numerical computation is needed
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning if comparing values or entities
        comparison_result = await self.comparison_reasoning()

        # Step 6: Ensemble all solutions to pick the best one
        solutions = [initial_answer, refined_answer, sequential_reasoning, arithmetic_result, comparison_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer