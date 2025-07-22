# Workflow ID: drop_97_0
# Benchmark: drop
# Data Indices: [2904, 3809, 2509, 3769, 3796]

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
        Starts with direct answer generation, then refines using review.
        Ensemble of multiple reasoning paths ensures robustness.
        """
        # Step 1: Generate initial answer directly
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to refine it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom reasoning to explore alternative solutions via iterative refinement
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Carefully analyze the problem step-by-step and iteratively improve your solution",
            reasoning_pattern="iterative",
            steps=["understand_problem", "extract_key_data", "reason_step_by_step", "verify_solution"],
            max_iterations=2
        )

        # Step 4: Ensemble all three solutions (original, reviewed, and iterative) to select the best one
        solutions = [initial_answer, refined_answer, iterative_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer