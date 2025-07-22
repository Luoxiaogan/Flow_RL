# Workflow ID: drop_818_0
# Benchmark: drop
# Data Indices: [3037, 2871, 623, 574]

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
        It uses specialized operators based on problem type and ensembles multiple solutions.
        """
        # Step 1: Generate an initial answer using direct reasoning
        solution1 = await self.answer_generate()

        # Step 2: Use custom reasoning to break down the problem step-by-step
        solution2 = await self.custom(instruction="Break down the problem into smaller steps and explain the reasoning behind each step.")

        # Step 3: Use flexible custom for structured, iterative refinement (e.g., for counting or arithmetic)
        solution3 = await self.flexible_custom(
            custom_instruction="Use iterative refinement to ensure accuracy in your solution.",
            reasoning_pattern="iterative",
            steps=["extract_key_info", "identify_operation", "compute_step_by_step", "verify_result"],
            max_iterations=2
        )

        # Step 4: Ensembling all three solutions to select the best one
        ensemble_solutions = [solution1, solution2, solution3]
        final_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_solution