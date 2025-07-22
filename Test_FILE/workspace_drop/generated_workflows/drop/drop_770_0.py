# Workflow ID: drop_770_0
# Benchmark: drop
# Data Indices: [3453, 680, 511, 3977]

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
        This is a workflow graph optimized for comprehensive reasoning.
        Uses multiple operators in parallel and sequential patterns to ensure robustness.
        """
        # Step 1: Generate initial answer using direct generation
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into detailed steps with clear reasoning for each",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_relevant_info", "perform_calculation", "verify_result"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        refined_answer = await self.flexible_custom(
            custom_instruction="Carefully analyze the problem and refine your answer through multiple iterations",
            reasoning_pattern="iterative",
            steps=["initial_solution", "check_consistency", "refine_if_needed"],
            max_iterations=3
        )

        # Step 4: Use comparison reasoning for problems involving max/min or relative values
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [initial_answer, step_by_step, refined_answer, comparison_result]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution