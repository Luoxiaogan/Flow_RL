# Workflow ID: gsm8k_66_1
# Benchmark: gsm8k
# Data Indices: [867, 153]

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
        This workflow uses a novel 'Reflect and Regenerate' pattern with a parallel ensemble twist.
        It first generates multiple initial solutions (parallel), then reflects on the best one,
        and finally regenerates a superior solution based on that reflection — all in under 6 steps.
        This is fundamentally different from iterative refinement: it leverages diversity of thought
        before applying meta-cognition to refine a single path.
        """

        # Step 1: Generate 3 diverse initial solutions using parallel strategies
        # Each uses a different reasoning prompt to encourage varied approaches
        solutions = [
            await self.custom(instruction="Solve step-by-step using basic arithmetic only."),
            await self.custom(instruction="Break the problem into smaller sub-problems and solve each individually."),
            await self.custom(instruction="Use algebraic modeling to represent unknowns and relationships.")
        ]

        # Step 2: Use ScEnsemble to select the best-performing solution from the three
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution — identify assumptions, gaps, or alternative interpretations
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a final answer using the reflection as guidance — this is the core "Reflect and Regenerate" loop
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. "
                        f"Reconstruct the solution with improved clarity, logical rigor, and attention to potential oversights."
        )

        return final_solution