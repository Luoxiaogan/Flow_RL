# Workflow ID: hotpotqa_162_0
# Benchmark: hotpotqa
# Data Indices: [3720, 3658, 1126, 164]

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
        Starts with an initial answer, then iteratively reviews and refines it using feedback from context.
        """
        # Step 1: Generate initial answer (hypothesis)
        initial_answer = await self.answer_generate()

        # Step 2: Use Review to refine the answer iteratively based on context
        refined_answer = initial_answer
        for _ in range(3):  # Perform 3 iterations of review/refinement
            reviewed_answer = await self.review(pre_solution=refined_answer)
            # If no improvement, break early to avoid unnecessary loops
            if reviewed_answer == refined_answer:
                break
            refined_answer = reviewed_answer

        # Step 3: Optional ensemble step – generate one more solution via custom reasoning and combine
        custom_solution = await self.custom(instruction="Break down the problem into smaller steps and reason through each step carefully.")
        
        # Ensemble the two solutions: original refined + custom step-by-step
        solutions = [refined_answer, custom_solution]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer