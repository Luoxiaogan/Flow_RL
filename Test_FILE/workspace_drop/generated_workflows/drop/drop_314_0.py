# Workflow ID: drop_314_0
# Benchmark: drop
# Data Indices: [2056, 2928, 3114, 110]

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
        Starts with direct answer generation, then refines via review.
        Uses ensemble to select best solution from multiple reasoning paths.
        """
        # Step 1: Generate initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer for refinement
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Generate alternative solutions using specialized operators
        counting_solution = await self.counting_reasoning()
        arithmetic_solution = await self.arithmetic_reasoning()
        comparison_solution = await self.comparison_reasoning()

        # Step 4: Ensemble all solutions to select the best one
        solutions = [
            initial_answer,
            refined_answer,
            counting_solution,
            arithmetic_solution,
            comparison_solution
        ]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer