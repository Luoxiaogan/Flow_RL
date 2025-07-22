# Workflow ID: gsm8k_281_1
# Benchmark: gsm8k
# Data Indices: [430, 562, 707]

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
        This workflow uses a novel combination of Parallel Ensemble + Reflect + Regenerate.
        It first generates 3 independent solutions in parallel (fan-out), selects the best one,
        then critically reflects on it to identify potential blind spots, and finally regenerates
        a refined solution based on that reflection — ensuring both robustness and meta-cognitive improvement.
        """

        # Step 1: Generate multiple diverse solutions using parallel ensemble
        # Each solution is generated with a different reasoning strategy via FlexibleCustom
        solutions = []
        strategies = [
            ("sequential", ["understand", "analyze", "compute", "verify"]),
            ("iterative", ["initial_approach", "refine", "finalize"], 2),
            ("branching", ["identify_knowns", "consider_alternatives", "choose_best"])
        ]

        for i, (pattern, steps, *args) in enumerate(strategies):
            max_iter = args[0] if args else 1
            sol = await self.flexible_custom(
                custom_instruction=f"Use a {pattern} approach to solve this problem.",
                reasoning_pattern=pattern,
                steps=steps,
                max_iterations=max_iter
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the most accurate solution from the pool
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect on the best solution to uncover hidden flaws or assumptions
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a new improved solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. "
                        f"Re-solve the problem by addressing any identified issues. Be precise and clear."
        )

        return final_answer