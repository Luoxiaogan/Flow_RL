# Workflow ID: hotpotqa_106_0
# Benchmark: hotpotqa
# Data Indices: [3649, 1097, 771, 744, 303]

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
        Starts with an initial answer, then iteratively reviews and refines it based on context.
        """
        # Step 1: Generate an initial answer (thought + answer)
        initial_answer = await self.answer_generate()
        
        # Step 2: Use iterative review to refine the answer
        refined_answer = initial_answer
        for i in range(3):  # Perform up to 3 iterations of refinement
            reviewed_answer = await self.review(pre_solution=refined_answer)
            if reviewed_answer == refined_answer:
                break  # No further improvement
            refined_answer = reviewed_answer

        # Step 3: Optionally ensemble with custom reasoning for robustness
        custom_reasoning = await self.custom(instruction="Break down the problem into smaller steps and explain each step clearly.")
        
        # Step 4: Ensemble the refined answer and custom reasoning to produce final solution
        solutions = [refined_answer, custom_reasoning]
        final_solution = await self.sc_ensemble(solutions=solutions)

        return final_solution