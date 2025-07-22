# Workflow ID: hotpotqa_552_0
# Benchmark: hotpotqa
# Data Indices: [577, 1854, 1954, 2532, 1060]

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
        This is a workflow graph for multi-hop question answering.
        It uses multiple reasoning paths and ensembles the best solution.
        """
        # Step 1: Generate initial answer using direct reasoning
        direct_answer = await self.answer_generate()

        # Step 2: Generate step-by-step reasoning with Custom
        step_by_step = await self.custom(instruction="Can you solve this problem by breaking it down into detailed steps and explaining the reasoning behind each step?")

        # Step 3: Use FlexibleCustom to explore multi-hop reasoning via iterative refinement
        iterative_refinement = await self.flexible_custom(
            custom_instruction="Start with an initial hypothesis and refine it iteratively based on evidence.",
            reasoning_pattern="iterative",
            steps=["initial_hypothesis", "verify_evidence", "refine_answer"],
            max_iterations=3
        )

        # Step 4: Ensemble the three solutions
        solutions = [direct_answer, step_by_step, iterative_refinement]
        final_answer = await self.sc_ensemble(solutions=solutions)

        # Step 5: Final review to catch any inconsistencies or errors
        final_solution = await self.review(pre_solution=final_answer)

        return final_solution