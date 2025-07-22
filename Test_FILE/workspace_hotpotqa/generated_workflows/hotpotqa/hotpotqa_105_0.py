# Workflow ID: hotpotqa_105_0
# Benchmark: hotpotqa
# Data Indices: [3796, 2052, 1542, 846]

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
        This is a workflow graph for multi-hop question answering using iterative refinement.
        Starts with an initial answer, then iteratively reviews and refines it.
        """
        # Step 1: Generate initial answer (hypothesis)
        initial_answer = await self.answer_generate()

        # Step 2: Iteratively refine the answer using Review
        refined_answer = initial_answer
        for i in range(3):  # 3 iterations of refinement
            review_result = await self.review(pre_solution=refined_answer)
            refined_answer = review_result

        # Step 3: Final ensemble to select best solution from multiple reasoning paths
        # Use FlexibleCustom with iterative pattern to explore multiple refinements
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Start with initial answer, then verify against context step by step",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "fact_verification", "answer_refinement"],
            max_iterations=3
        )

        # Ensemble the final refined answer with the iterative result
        solutions = [refined_answer, iterative_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)

        return final_answer