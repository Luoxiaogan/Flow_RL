# Workflow ID: drop_773_0
# Benchmark: drop
# Data Indices: [2044, 521, 676, 60]

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
        Uses flexible custom with sequential and parallel patterns to explore multiple reasoning paths,
        then ensembles the best result from diverse approaches.
        """
        # Step 1: Use FlexibleCustom in sequential mode for step-by-step breakdown
        seq_solution = await self.flexible_custom(
            custom_instruction="Break down the problem into clear, logical steps and explain each reasoning phase",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_information", "reason_step_by_step", "verify_conclusion"]
        )

        # Step 2: Use FlexibleCustom in parallel mode to generate alternative interpretations
        par_solution = await self.flexible_custom(
            custom_instruction="Explore multiple reasoning paths independently and synthesize insights",
            reasoning_pattern="parallel",
            steps=["analyze_from_different_perspectives", "compare_approaches", "integrate_insights"]
        )

        # Step 3: Use specialized operators for domain-specific tasks (counting, arithmetic, comparison)
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Generate direct answer as baseline
        direct_answer = await self.answer_generate()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            seq_solution,
            par_solution,
            counting_result,
            arithmetic_result,
            comparison_result,
            direct_answer
        ]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution