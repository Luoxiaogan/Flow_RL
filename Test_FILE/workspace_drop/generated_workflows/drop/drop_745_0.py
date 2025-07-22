# Workflow ID: drop_745_0
# Benchmark: drop
# Data Indices: [1800, 151, 3503, 343]

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
        Uses multiple operators with different patterns to ensure robustness.
        """
        # Step 1: Get initial answer via direct generation
        initial_answer = await self.answer_generate()

        # Step 2: Generate alternative reasoning paths using FlexibleCustom (sequential and parallel)
        sequential_reasoning = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step with clear reasoning at each stage",
            reasoning_pattern="sequential",
            steps=["understand_question", "extract_key_info", "apply_logic", "verify_solution"]
        )

        parallel_approach = await self.flexible_custom(
            custom_instruction="Explore multiple reasoning strategies simultaneously and compare results",
            reasoning_pattern="parallel",
            steps=["identify_core_task", "generate_multiple_solutions", "evaluate_consistency"]
        )

        # Step 3: Use specialized operators for structured tasks
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 4: Ensemble all solutions to find the best one
        solution_list = [
            initial_answer,
            sequential_reasoning,
            parallel_approach,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        ensembled_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 5: Final review to refine the ensemble result
        final_answer = await self.review(pre_solution=ensembled_solution)

        return final_answer