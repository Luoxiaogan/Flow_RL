# Workflow ID: gsm8k_159_1
# Benchmark: gsm8k
# Data Indices: [143, 760]

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
        Diverse workflow using the Iterative Refinement pattern with a clear progression:
        1. Generate an initial solution using a simple Custom call.
        2. Apply Review twice to progressively refine the solution — each time improving clarity, logic, or completeness.
        3. Return the final refined answer.
        
        This approach avoids complex structures like ensembling or reflection-based regeneration, focusing instead on stepwise improvement through direct critique (Review).
        """
        # Step 1: Generate a basic initial solution
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all reasoning clearly."
        )

        # Step 2: Apply iterative refinement via Review (at least two times)
        first_refinement = await self.review(pre_solution=initial_solution)
        second_refinement = await self.review(pre_solution=first_refinement)

        # Step 3: Return the final improved solution
        return second_refinement