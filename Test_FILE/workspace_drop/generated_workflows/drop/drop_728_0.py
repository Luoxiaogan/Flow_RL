# Workflow ID: drop_728_0
# Benchmark: drop
# Data Indices: [71, 2421, 3058, 472]

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
        Uses multiple specialized operators with ensemble and review to improve accuracy.
        """
        # Step 1: Get initial answer from direct generation
        initial_answer = await self.answer_generate()

        # Step 2: Use flexible custom with sequential reasoning for structured breakdown
        structured_analysis = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step with clear reasoning at each stage",
            reasoning_pattern="sequential",
            steps=["identify_key_elements", "extract_numerical_data", "apply_logic", "generate_final_answer"]
        )

        # Step 3: Use counting reasoning if the problem involves counting (e.g., events, items)
        counting_result = await self.counting_reasoning()

        # Step 4: Use arithmetic reasoning for numerical computations
        arithmetic_result = await self.arithmetic_reasoning()

        # Step 5: Use comparison reasoning for max/min or relative comparisons
        comparison_result = await self.comparison_reasoning()

        # Step 6: Review the initial answer using a dedicated review agent
        reviewed_answer = await self.review(pre_solution=initial_answer)

        # Step 7: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            structured_analysis,
            counting_result,
            arithmetic_result,
            comparison_result,
            reviewed_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution