# Workflow ID: gsm8k_386_0
# Benchmark: gsm8k
# Data Indices: [780, 233]

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
        Diverse and effective workflow combining Parallel Ensemble + Reflect-and-Regenerate.
        Step 1: Generate 3 independent solutions via parallel ensemble.
        Step 2: Select the best one using ScEnsemble.
        Step 3: Reflect on the selected solution to identify potential flaws or missed assumptions.
        Step 4: Use that reflection to guide a new Custom call for an improved final answer.
        """
        # --- PARALLEL ENSEMBLE ---
        solutions = []
        for i in range(3):  # Generate 3 diverse initial approaches
            solution = await self.custom(
                instruction="Solve this math word problem by breaking it into clear steps. Focus on identifying known quantities, unknowns, and relationships between them."
            )
            solutions.append(solution)

        # --- SELECT BEST SOLUTION ---
        best_solution = await self.sc_ensemble(solutions=solutions)

        # --- REFLECT ON THE BEST SOLUTION ---
        reflection = await self.reflect(pre_solution=best_solution)

        # --- REGENERATE BASED ON REFLECTION ---
        final_answer = await self.custom(
            instruction=f"Given the following solution and reflection: {reflection}. Now, provide a revised, improved solution that addresses any weaknesses or ambiguities identified in the reflection."
        )

        return final_answer