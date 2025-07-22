# Workflow ID: gsm8k_359_1
# Benchmark: gsm8k
# Data Indices: [278, 147]

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
        This design combines two distinct patterns:
        1. Parallel Ensemble: Generate 3 diverse solutions using different reasoning styles.
        2. Reflect-and-Regenerate: Critically reflect on the best solution, then regenerate a refined version based on that reflection — mimicking meta-cognitive learning.

        Why it's different from the existing workflow:
        - Uses parallel generation (not sequential refinement)
        - Introduces reflective critique before final regen (not just repeated review)
        - Leverages FlexibleCustom in 'parallel' mode for structured diversity
        - Combines ensemble selection with targeted regeneration
        """

        # Step 1: Generate multiple candidate solutions via parallel reasoning
        # Use FlexibleCustom in "parallel" mode to explore different strategies
        parallel_solutions = []
        for i in range(3):
            solution = await self.flexible_custom(
                custom_instruction="Use a unique reasoning approach each time.",
                reasoning_pattern="parallel",
                steps=["analyze", "plan", "solve", "verify"],
                use_structured_output=True
            )
            parallel_solutions.append(solution)

        # Step 2: Select the best solution using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=parallel_solutions)

        # Step 3: Reflect critically on the selected solution — identify potential flaws or improvements
        reflection_text = await self.reflect(pre_solution=best_solution)

        # Step 4: Regenerate a new solution guided by the reflection
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection_text}'. "
                        f"Now, synthesize a more accurate and logically sound answer."
        )

        return final_solution