# Workflow ID: drop_445_0
# Benchmark: drop
# Data Indices: [2739, 1710, 3363, 725, 3652]

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
        This is a comprehensive workflow graph for reading comprehension and discrete reasoning.
        It uses multiple reasoning strategies (sequential, parallel, iterative) and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning to break down steps
        step_by_step_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps with detailed reasoning for each",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_evidence", "reason_stepwise", "verify_consistency"]
        )

        # Step 3: Use flexible custom with iterative refinement for accuracy
        refined_answer = await self.flexible_custom(
            custom_instruction="Carefully count or compute the required value, double-checking for errors",
            reasoning_pattern="iterative",
            steps=["initial_calculation", "verify_completeness", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Use comparison reasoning if the problem involves ranking or ordering
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensembe all solutions to select the most reliable one
        solutions = [
            initial_answer,
            step_by_step_analysis,
            refined_answer,
            comparison_result
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution