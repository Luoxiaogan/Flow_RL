# Workflow ID: gsm8k_203_1
# Benchmark: gsm8k
# Data Indices: [463, 211, 387]

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
        Diverse workflow combining Parallel Ensemble with Reflect-and-Regenerate logic.
        This approach first explores multiple solution strategies in parallel (fan-out),
        then selects the best candidate using ensemble scoring, and finally applies meta-cognitive reflection
        to refine that top solution — creating a two-stage improvement loop: diversity → selection → deep refinement.
        """

        # Step 1: Generate 3 independent solutions using different reasoning patterns (Parallel Ensemble)
        solutions = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            sol = await self.flexible_custom(
                reasoning_pattern=pattern,
                steps=["analyze", "plan", "solve", "verify"],
                custom_instruction="Solve this math problem by applying a structured approach appropriate to your chosen reasoning pattern."
            )
            solutions.append(sol)

        # Step 2: Use ScEnsemble to select the most promising solution from the parallel candidates
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Critically reflect on the best solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Based on the reflection, generate a final improved version of the solution
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the best solution: '{reflection}'. Now, synthesize a new, more accurate answer that addresses all identified concerns. Be precise and step-by-step."
        )

        return final_answer