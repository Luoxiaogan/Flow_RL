# Workflow ID: drop_6_0
# Benchmark: drop
# Data Indices: [1021, 3534, 3892, 617]

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
        Starts with direct answer generation, then refines via review.
        Uses ensemble to combine multiple reasoning paths when needed.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to refine it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: If the problem involves counting, use CountingReasoning
        count_result = await self.counting_reasoning()
        
        # Step 4: If arithmetic is involved, use ArithmeticReasoning
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: If comparison is required, use ComparisonReasoning
        comparison_result = await self.comparison_reasoning()

        # Step 6: Use FlexibleCustom for complex reasoning patterns (iterative refinement)
        flexible_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step by step and reason iteratively",
            reasoning_pattern="iterative",
            steps=["analyze_question", "extract_key_info", "reason_stepwise", "verify_final_answer"],
            max_iterations=2
        )

        # Step 7: Ensemble multiple solutions (including refined and flexible ones) for robustness
        solutions = [
            initial_answer,
            refined_answer,
            flexible_solution,
            count_result if count_result else "",
            arithmetic_result if arithmetic_result else "",
            comparison_result if comparison_result else ""
        ]
        # Filter out empty strings before ensembling
        valid_solutions = [s for s in solutions if s.strip()]
        if len(valid_solutions) > 1:
            final_solution = await self.sc_ensemble(solutions=valid_solutions)
        else:
            final_solution = valid_solutions[0] if valid_solutions else refined_answer

        return final_solution