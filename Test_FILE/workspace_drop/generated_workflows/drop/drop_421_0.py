# Workflow ID: drop_421_0
# Benchmark: drop
# Data Indices: [313, 1470, 390, 2479]

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
        This is a robust workflow graph using Parallel Ensemble pattern.
        Generates multiple solutions via different reasoning approaches,
        then selects the best one using ScEnsemble for improved accuracy.
        """
        # Generate diverse solutions using different reasoning strategies
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Break down the problem step by step and explain each reasoning step clearly.")
        
        solution3 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to solve this step-by-step with verification at each stage.",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_question_type", "apply_logic", "verify_solution"]
        )
        
        solution4 = await self.flexible_custom(
            custom_instruction="Use iterative refinement to count or compute carefully and double-check your answer.",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "refine_result", "final_verification"],
            max_iterations=2
        )

        # Ensemble all solutions to find the most consistent and accurate answer
        solutions = [solution1, solution2, solution3, solution4]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer