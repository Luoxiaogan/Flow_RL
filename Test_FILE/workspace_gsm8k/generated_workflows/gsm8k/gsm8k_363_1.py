# Workflow ID: gsm8k_363_1
# Benchmark: gsm8k
# Data Indices: [414, 136]

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
        Novel workflow combining Parallel Ensemble + Reflect + Regenerate logic.
        This structure first explores multiple solution paths (parallel), selects the best one,
        then uses reflection to guide a targeted re-solution — creating a meta-cognitive loop
        that is fundamentally different from the existing single-path iterative approach.
        """
        # Step 1: Generate 3 independent solutions using parallel reasoning (fan-out)
        solutions = []
        for i in range(3):
            sol = await self.flexible_custom(
                custom_instruction="Solve this math problem by considering one unique strategy per attempt.",
                reasoning_pattern="parallel",
                steps=["identify", "calculate", "verify"]
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the best solution among the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to generate a final, improved solution via Custom
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}', "
                       f"provide a refined answer that addresses any identified weaknesses or gaps."
        )

        return final_answer