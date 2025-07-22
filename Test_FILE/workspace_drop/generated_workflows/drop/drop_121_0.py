# Workflow ID: drop_121_0
# Benchmark: drop
# Data Indices: [518, 179, 2754, 2030]

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
        This is a workflow graph using Parallel Ensemble pattern for robustness.
        Generates multiple solutions via different reasoning paths, then ensembles the best one.
        """
        # Generate multiple distinct solutions using different operators
        solution1 = await self.answer_generate()
        solution2 = await self.counting_reasoning()
        solution3 = await self.arithmetic_reasoning()
        solution4 = await self.comparison_reasoning()

        # Use FlexibleCustom to generate a structured, step-by-step solution
        solution5 = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps and reason through each one",
            reasoning_pattern="sequential",
            steps=["extract_key_info", "identify_task_type", "apply_logic", "verify_solution"]
        )

        # Also use Custom with a step-by-step instruction for additional diversity
        solution6 = await self.custom(
            instruction="Solve this by breaking it down into smaller logical steps and explaining each step clearly."
        )

        # Ensemble all six solutions to select the most consistent and accurate answer
        solutions = [solution1, solution2, solution3, solution4, solution5, solution6]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer