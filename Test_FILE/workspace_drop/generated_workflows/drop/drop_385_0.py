# Workflow ID: drop_385_0
# Benchmark: drop
# Data Indices: [1708, 2426, 2206, 3534]

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
        This is a workflow graph using Parallel Ensemble for robustness.
        Generates multiple solutions via different reasoning paths, then selects the best one.
        """
        # Generate 3 diverse solutions using different operators
        solution1 = await self.answer_generate()
        
        solution2 = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")
        
        solution3 = await self.flexible_custom(
            custom_instruction="Use iterative refinement to carefully analyze the problem and improve the answer",
            reasoning_pattern="iterative",
            steps=["extract_key_info", "identify_operation", "compute_step_by_step", "verify_solution"],
            max_iterations=2
        )
        
        # Ensemble the three solutions to pick the most consistent and accurate one
        solutions = [solution1, solution2, solution3]
        final_answer = await self.sc_ensemble(solutions=solutions)
        
        return final_answer