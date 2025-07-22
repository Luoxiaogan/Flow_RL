# Workflow ID: gsm8k_254_1
# Benchmark: gsm8k
# Data Indices: [308, 490, 249]

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
        This is a diverse and efficient workflow using parallel ensemble with iterative refinement.
        It generates multiple initial solutions in parallel, then refines the best one through review.
        This avoids single-point failure and ensures robustness without excessive complexity.
        """

        # Step 1: Generate three independent solutions using parallel reasoning
        solution_a = await self.custom(instruction="Solve the problem step-by-step, focusing on clear arithmetic operations.")
        solution_b = await self.custom(instruction="Break down the problem into smaller steps and solve each part carefully.")
        solution_c = await self.custom(instruction="Apply basic math principles systematically—identify knowns, unknowns, and operations.")

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution_a, solution_b, solution_c])

        # Step 3: Critically review the best solution to catch any remaining errors or ambiguities
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution