# Workflow ID: gsm8k_114_1
# Benchmark: gsm8k
# Data Indices: [215, 507, 350]

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
        This workflow uses the Iterative Refinement pattern with a clear progression:
        1. Generate an initial solution.
        2. Apply Review twice to progressively refine it — each iteration improves clarity, logic, and completeness.
        3. Return the final refined solution.
        
        This approach avoids reflection-based meta-cognition in favor of direct iterative improvement via structured review.
        It's simple, effective, and logically distinct from the existing workflow that uses reflection + regen.
        """
        # Step 1: Initial solution using general reasoning instruction
        solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations clearly."
        )

        # Step 2: First refinement pass — improve structure and correctness
        solution = await self.review(pre_solution=solution)

        # Step 3: Second refinement pass — enhance clarity and eliminate ambiguity
        solution = await self.review(pre_solution=solution)

        return solution