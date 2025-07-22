# Workflow ID: drop_114_0
# Benchmark: drop
# Data Indices: [1098, 491, 538, 2077]

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
        Starts with a direct answer, then refines it via review, and finally ensembles multiple reasoning approaches.
        """
        # Step 1: Generate initial answer
        initial_answer = await self.answer_generate()
        
        # Step 2: Review the initial answer to improve accuracy
        refined_answer = await self.review(pre_solution=initial_answer)
        
        # Step 3: Use flexible custom to perform step-by-step reasoning (sequential pattern)
        step_by_step_answer = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and reason through each one carefully",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_data", "apply_logic", "verify_result"]
        )
        
        # Step 4: Ensembling to select the best solution from multiple approaches
        solutions = [initial_answer, refined_answer, step_by_step_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer