# Workflow ID: gsm8k_105_0
# Benchmark: gsm8k
# Data Indices: [560, 965]

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
        This is a diverse and complex workflow combining:
        1. Parallel Ensemble (fan-out) to generate multiple initial solutions
        2. Reflect and Regenerate pattern: Critique the best solution and use that insight to improve it
        3. Iterative Refinement on the improved solution for final polish
        """

        # Step 1: Generate 3 independent solutions using parallel ensemble
        solution_list = []
        for i in range(3):
            solution = await self.custom(
                instruction="Solve the problem step-by-step, explaining your reasoning clearly. Do not assume any prior knowledge."
            )
            solution_list.append(solution)

        # Step 2: Use ScEnsemble to pick the most accurate of the three
        best_solution = await self.sc_ensemble(solutions=solution_list)

        # Step 3: Reflect critically on the best solution — identify assumptions, gaps, or alternative approaches
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a new Custom call for a refined solution
        improved_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem with this critique in mind. Be more precise and address potential weaknesses."
        )

        # Step 5: Apply iterative refinement to polish the improved solution
        final_solution = improved_solution
        for _ in range(2):  # Two rounds of review/refinement
            revised = await self.review(pre_solution=final_solution)
            if revised == final_solution:  # No change means we're done
                break
            final_solution = revised

        return final_solution