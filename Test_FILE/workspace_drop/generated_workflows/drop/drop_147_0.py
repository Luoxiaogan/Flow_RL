# Workflow ID: drop_147_0
# Benchmark: drop
# Data Indices: [1521, 415, 1053, 2512, 2674]

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

        # Step 2: Review the initial solution to refine it
        refined_solution = await self.review(pre_solution=initial_solution)

        # Step 3: Use flexible custom to generate alternative reasoning paths (iterative refinement)
        iterative_solution = await self.flexible_custom(
            custom_instruction="Break down the problem step-by-step and verify each step",
            reasoning_pattern="iterative",
            steps=["understand_question", "extract_info", "reason_stepwise", "verify_final_answer"],
            max_iterations=2
        )

        # Step 4: Ensemble all three solutions to select the best one
        ensemble_solutions = [initial_solution, refined_solution, iterative_solution]
        final_solution = await self.sc_ensemble(solutions=ensemble_solutions)

        return final_solution