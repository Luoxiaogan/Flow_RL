# Workflow ID: drop_822_0
# Benchmark: drop
# Data Indices: [3031, 2006, 1850, 1796]

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
        This is a comprehensive reasoning workflow for reading comprehension and discrete reasoning.
        It uses multiple specialized operators and ensembles their results to improve accuracy.
        """
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for step-by-step breakdown
        sequential_analysis = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["extract_key_events", "identify_numerical_data", "perform_step_by_step_calculation"],
            custom_instruction="Break down the problem into clear steps and explain each reasoning step thoroughly."
        )

        # Step 3: Use flexible custom with iterative refinement for count-based problems
        iterative_count = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["initial_count", "verify_completeness", "refine_answer"],
            max_iterations=3,
            custom_instruction="Carefully count all relevant entities or events, then double-check for completeness."
        )

        # Step 4: Use comparison reasoning for problems involving max/min or relative values
        comparison_result = await self.comparison_reasoning()

        # Step 5: Use arithmetic reasoning for numerical computations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 6: Review the initial answer for potential errors
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 7: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            sequential_analysis,
            iterative_count,
            comparison_result,
            arithmetic_result,
            reviewed_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution