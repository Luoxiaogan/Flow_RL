# Workflow ID: drop_256_0
# Benchmark: drop
# Data Indices: [2286, 2055, 3159, 2570, 1764]

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
        Generates multiple solutions via different reasoning approaches and selects the best one.
        """
        # Generate 3 diverse solutions using different reasoning strategies
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Break down the problem step by step with clear reasoning for each step.")
        
        solution3 = await self.flexible_custom(
            custom_instruction="Use sequential reasoning to solve this problem carefully.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_info", "reason_step_by_step", "verify_solution"]
        )
        
        # Ensemblers the three solutions to select the most consistent answer
        solutions = [solution1, solution2, solution3]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer