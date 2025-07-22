# Workflow ID: gsm8k_220_1
# Benchmark: gsm8k
# Data Indices: [961, 221, 244]

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
        This is a diverse and efficient workflow using the Parallel Ensemble pattern.
        It generates three independent solutions using different reasoning strategies,
        then selects the best one using ScEnsemble — ensuring robustness against single-point failures.
        This approach differs fundamentally from the Reflect-and-Regenerate logic by prioritizing diversity of thought over iterative refinement.
        """
        # Step 1: Generate multiple solutions in parallel using different prompts
        solution1 = await self.custom(instruction="Solve the problem by first identifying all given quantities and relationships.")
        solution2 = await self.custom(instruction="Break the problem into smaller sub-problems and solve each step-by-step.")
        solution3 = await self.custom(instruction="Use dimensional analysis or unit-based reasoning to ensure correctness.")

        # Step 2: Use ScEnsemble to select the most accurate solution from the three
        final_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return final_solution