# Workflow ID: gsm8k_118_1
# Benchmark: gsm8k
# Data Indices: [770, 974, 788]

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
        This is a diverse and efficient workflow using the Parallel Ensemble + Reflect + Regenerate pattern.
        It first generates multiple independent solutions (parallel), selects the best one (ensemble),
        then reflects on it to uncover hidden assumptions or errors, and finally regenerates a refined solution
        based on that reflection — all in under 6 steps. This introduces both parallel exploration and meta-cognitive refinement.
        """

        # Step 1: Generate 3 independent solutions using different reasoning strategies via FlexibleCustom
        # Each uses a unique "reasoning_pattern" to explore different paths
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            fc = operator.FlexibleCustom(
                self.config, 
                self.problem,
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                max_iterations=2 if pattern == "iterative" else 1
            )
            sol = await fc(custom_instruction="Solve this math problem with a clear, structured approach.")
            solutions.append(sol)

        # Step 2: Use ScEnsemble to pick the most accurate of the three initial attempts
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a new, improved solution
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        "Now, synthesize this insight into a new, more robust and accurate answer."
        )

        return final_solution