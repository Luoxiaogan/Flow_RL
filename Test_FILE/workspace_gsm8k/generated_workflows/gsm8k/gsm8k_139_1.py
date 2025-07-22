# Workflow ID: gsm8k_139_1
# Benchmark: gsm8k
# Data Indices: [841, 670, 812]

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
        This is a diverse and effective workflow using the 'Parallel Ensemble' pattern.
        It generates multiple independent solutions in parallel, then selects the best one.
        This approach improves robustness by leveraging diversity in reasoning strategies.
        """
        # Step 1: Generate 3 independent solutions using different reasoning styles
        solution1 = await self.custom(
            instruction="Solve the problem step-by-step using a clear, linear approach. Break it into small logical steps."
        )
        solution2 = await self.custom(
            instruction="Solve the problem by first identifying all known quantities and unknowns, then applying relevant formulas or logic."
        )
        solution3 = await self.custom(
            instruction="Solve the problem using a structured method: define variables, set up equations, solve them, and verify the answer."
        )

        # Step 2: Use ScEnsemble to evaluate and select the best solution from the three
        best_solution = await self.sc_ensemble(solutions=[solution1, solution2, solution3])

        return best_solution