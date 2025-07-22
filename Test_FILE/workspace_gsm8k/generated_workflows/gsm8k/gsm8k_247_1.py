# Workflow ID: gsm8k_247_1
# Benchmark: gsm8k
# Data Indices: [868, 454, 620]

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
        self.review = operator.Review(self.config, self.problem)
        self.reflect = operator.Reflect(self.config, self.problem)
        self.flexible_custom = operator.FlexibleCustom(self.config, self.problem)

    async def run_workflow(self):
        """
        This is a diverse and robust workflow using the Iterative Refinement pattern.
        Starts with a simple solution, then applies Review at least twice to progressively improve it.
        Uses no ensembling or parallel strategies — instead, focuses on deepening reasoning through repetition.
        """
        # Step 1: Generate an initial solution using basic step-by-step instruction
        initial_solution = await self.custom(instruction="Solve the problem by breaking it down into clear, sequential steps. Show all calculations.")

        # Step 2: First refinement pass – review the initial solution for clarity, correctness, and completeness
        first_refined = await self.review(pre_solution=initial_solution)

        # Step 3: Second refinement pass – apply another round of review to catch subtler issues
        second_refined = await self.review(pre_solution=first_refined)

        # Step 4: Optional final polish — reflect on the solution to ensure it's logically sound before returning
        reflection = await self.reflect(pre_solution=second_refined)
        final_answer = await self.custom(instruction=f"Based on the following reflection:\n{reflection}\nRevise the solution one last time to ensure it is accurate, complete, and well-explained.")

        return final_answer