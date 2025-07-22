# Workflow ID: drop_170_0
# Benchmark: drop
# Data Indices: [3107, 2984, 232, 526, 2299]

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
        This is a comprehensive reasoning workflow that combines multiple operators
        to handle diverse reading comprehension and discrete reasoning tasks.
        """
        # Step 1: Generate an initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for detailed step-by-step breakdown
        detailed_step_by_step = await self.flexible_custom(
            custom_instruction="Break down the problem into smaller steps and explain each reasoning step clearly.",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_solution"]
        )

        # Step 3: Use flexible custom with iterative refinement for count-based problems
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Carefully count all relevant items and double-check your result.",
            reasoning_pattern="iterative",
            steps=["identify_items_to_count", "count_once", "verify_completeness", "refine_if_needed"],
            max_iterations=3
        )

        # Step 4: Use comparison reasoning for problems involving max/min or ranking
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble the three most promising solutions
        solutions = [
            initial_answer,
            detailed_step_by_step,
            iterative_refinement,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer