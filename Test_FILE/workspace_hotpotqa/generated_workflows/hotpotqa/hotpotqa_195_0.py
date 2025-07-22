# Workflow ID: hotpotqa_195_0
# Benchmark: hotpotqa
# Data Indices: [3854, 1248, 2196, 1121]

class Workflow:
    def __init__(
        self,
        config,
        problem
    ) -> None:
        self.problem = problem
        self.config = create(config)
        self.custom = operator.Custom(self.config, self.problem)
        self.sc_ensemble = operator.ScEnsemble(self.config, self.problem)
        self.answer_generate = operator.AnswerGenerate(self.config, self.problem)
        self.review = operator.Review(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a workflow graph for multi-hop question answering with iterative refinement.
        Starts with an initial answer, then iteratively reviews and refines it using the context.
        """
        # Step 1: Generate an initial answer (hypothesis)
        initial_answer = await self.answer_generate()

        # Step 2: Use iterative review to refine the answer based on context
        refined_answer = initial_answer
        for _ in range(3):  # Iterative refinement loop (3 iterations max)
            reviewed_answer = await self.review(pre_solution=refined_answer)
            refined_answer = reviewed_answer

        # Step 3: Optionally ensemble with alternative reasoning paths (if needed)
        # Generate one alternative solution via Custom (step-by-step breakdown)
        step_by_step_solution = await self.custom(
            instruction="Break down the problem into smaller steps and explain the reasoning behind each step."
        )

        # Ensemble the original refined answer with the step-by-step version
        solutions = [refined_answer, step_by_step_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer