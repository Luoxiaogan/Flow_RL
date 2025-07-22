# Workflow ID: drop_46_0
# Benchmark: drop
# Data Indices: [2594, 2173, 1522, 3564]

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
        # Step 1: Generate initial answer using direct reasoning
        initial_answer = await self.answer_generate()

        # Step 2: Review the initial answer to refine it
        refined_answer = await self.review(pre_solution=initial_answer)

        # Step 3: Use flexible custom to perform iterative refinement (e.g., count or compare based on problem type)
        iterative_answer = await self.flexible_custom(
            custom_instruction="Perform step-by-step reasoning and iterative verification",
            reasoning_pattern="iterative",
            steps=["extract_key_info", "identify_task_type", "solve_stepwise", "verify_result"],
            max_iterations=2
        )

        # Step 4: Ensemble multiple solutions to get the most accurate result
        solutions = [initial_answer, refined_answer, iterative_answer]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer