# Workflow ID: drop_890_0
# Benchmark: drop
# Data Indices: [1669, 475, 3210, 3669]

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
        Uses flexible custom reasoning patterns and ensemble to improve accuracy.
        """
        # Step 1: Generate initial answer using direct generation
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "formulate_answer"]
        )

        # Step 3: Use flexible custom with iterative reasoning for refinement
        refined_answer = await self.flexible_custom(
            custom_instruction="Refine the solution by checking for completeness and correctness",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "identify_gaps", "improve_solution"],
            max_iterations=2
        )

        # Step 4: Review the best candidate to improve confidence
        reviewed_answer = await self.review(pre_solution=refined_answer)

        # Step 5: Ensemble multiple solutions (including original, step-by-step, and refined)
        solutions = [initial_answer, step_by_step, reviewed_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer