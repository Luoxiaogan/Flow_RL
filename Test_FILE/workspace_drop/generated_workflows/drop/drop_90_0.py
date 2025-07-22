# Workflow ID: drop_90_0
# Benchmark: drop
# Data Indices: [1516, 2320, 3371, 2884]

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
        This is a workflow graph optimized for iterative improvement.
        Starts with direct answer generation, then refines via review,
        and finally ensembles multiple reasoning approaches for robustness.
        """
        # Step 1: Generate initial solution
        initial_solution = await self.answer_generate()

        # Step 2: Review to refine the initial solution
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Use flexible custom for iterative refinement (e.g., counting or arithmetic)
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and verify each step carefully",
            reasoning_pattern="iterative",
            steps=["extract_key_info", "identify_operation", "perform_calculation", "verify_result"],
            max_iterations=2
        )

        # Step 4: Generate additional solutions using specialized operators
        counting_result = await self.counting_reasoning()
        arithmetic_result = await self.arithmetic_reasoning()
        comparison_result = await self.comparison_reasoning()

        # Step 5: Ensemble all solutions to select the best one
        solutions = [
            initial_solution,
            refined_solution,
            iterative_refinement,
            counting_result,
            arithmetic_result,
            comparison_result
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer