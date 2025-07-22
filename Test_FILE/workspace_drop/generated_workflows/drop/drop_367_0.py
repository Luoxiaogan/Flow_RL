# Workflow ID: drop_367_0
# Benchmark: drop
# Data Indices: [2017, 2225, 757, 3493, 3956]

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
        This is a comprehensive workflow graph optimized for reading comprehension and discrete reasoning.
        It uses multiple reasoning strategies (sequential, parallel, iterative) with ensemble selection to ensure robustness.
        """
        # Step 1: Generate baseline answer
        baseline = await self.answer_generate()

        # Step 2: Use flexible custom with sequential pattern for step-by-step breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_result"]
        )

        # Step 3: Use flexible custom with iterative pattern for refinement
        iter_solution = await self.flexible_custom(
            custom_instruction="Carefully count or compute, then refine your answer by checking for errors",
            reasoning_pattern="iterative",
            steps=["initial_answer", "check_for_errors", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Use specialized operators for domain-specific tasks
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [baseline, seq_solution, iter_solution, counting_result, arithmetic_result, comparison_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer