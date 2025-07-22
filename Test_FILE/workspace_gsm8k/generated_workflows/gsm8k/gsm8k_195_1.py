# Workflow ID: gsm8k_195_1
# Benchmark: gsm8k
# Data Indices: [709, 46, 761]

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
        Hybrid Workflow: Parallel Ensemble + Reflect-and-Regenerate
        1. Generate 3 diverse initial solutions using parallel reasoning.
        2. Use ScEnsemble to select the best one.
        3. Critically reflect on that solution's potential flaws or assumptions.
        4. Use the reflection to guide a targeted regeneration of the final answer.
        This combines robustness (parallel) with meta-cognition (reflection) for higher-quality outcomes.
        """
        # Step 1: Generate multiple independent solutions in parallel
        solution_candidates = []
        for _ in range(3):
            candidate = await self.flexible_custom(
                reasoning_pattern="sequential",
                steps=["identify_unknowns", "formulate_equation", "solve", "verify"],
                custom_instruction="Solve this math problem by first identifying all known and unknown quantities."
            )
            solution_candidates.append(candidate)

        # Step 2: Select the most accurate solution from the ensemble
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Reflect critically on the best solution — identify possible weaknesses
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate the final answer based on the reflection
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the previous solution: '{reflection}'. "
                       f"Re-evaluate the problem carefully and provide a new, improved final answer."
        )

        return final_answer