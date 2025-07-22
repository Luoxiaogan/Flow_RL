# Workflow ID: drop_180_0
# Benchmark: drop
# Data Indices: [3576, 1723, 2182, 798]

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
        Starts with a direct answer, then refines it through review and ensemble.
        """
        # Step 1: Generate initial answer using AnswerGenerate
        initial_answer = await self.answer_generate()
        
        # Step 2: Review the initial answer to refine it
        refined_answer = await self.review(pre_solution=initial_answer)
        
        # Step 3: Use flexible custom reasoning for structured step-by-step verification
        structured_verification = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and verify each one carefully",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_relevant_info", "perform_calculation", "verify_final_answer"]
        )
        
        # Step 4: Ensemble all three solutions (initial, refined, structured) to select the best
        solutions = [initial_answer, refined_answer, structured_verification]
        final_solution = await self.sc_ensemble(solutions=solutions)
        
        return final_solution