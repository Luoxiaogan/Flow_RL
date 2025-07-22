# Workflow ID: drop_327_0
# Benchmark: drop
# Data Indices: [855, 3115, 1840, 317, 720]

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
        This is a comprehensive reasoning workflow that uses multiple operators
        to generate and refine solutions for reading comprehension and discrete reasoning problems.
        It leverages specialized reasoning types (counting, arithmetic, comparison) 
        alongside flexible custom reasoning patterns (sequential, iterative) and ensembling.
        """
        # Step 1: Generate base answer using direct reasoning
        base_answer = await self.answer_generate()

        # Step 2: Use FlexibleCustom with sequential pattern for step-by-step breakdown
        sequential_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into detailed steps and explain the reasoning behind each step",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_evidence", "reason_step_by_step", "verify_solution"]
        )

        # Step 3: Use FlexibleCustom with iterative pattern for refinement
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Carefully count or calculate, then double-check your result for completeness",
            reasoning_pattern="iterative",
            steps=["initial_analysis", "verify_accuracy", "refine_answer"],
            max_iterations=2
        )

        # Step 4: Specialized operators for specific tasks
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all results to select best solution
        solutions = [
            base_answer,
            sequential_analysis,
            iterative_refinement,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution