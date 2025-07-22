# Workflow ID: drop_411_0
# Benchmark: drop
# Data Indices: [2484, 106, 1026, 3296, 349]

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
        This is a comprehensive reasoning workflow for reading comprehension and discrete problems.
        Uses multiple operators in parallel and sequential patterns to ensure robustness.
        """
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        sequential_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear steps with detailed reasoning",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_data", "reason_step_by_step", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        iterative_solution = await self.flexible_custom(
            custom_instruction="Carefully analyze and refine your solution through multiple iterations",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "identify_assumptions", "refine_reasoning"],
            max_iterations=3
        )

        # Step 4: Use comparison reasoning for value-based questions (e.g., largest group, shortest field goal)
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [direct_answer, sequential_solution, iterative_solution, comparison_result]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer