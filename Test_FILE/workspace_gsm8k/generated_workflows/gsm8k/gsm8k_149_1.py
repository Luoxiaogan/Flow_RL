# Workflow ID: gsm8k_149_1
# Benchmark: gsm8k
# Data Indices: [480, 15]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern combined with Parallel Ensemble.
        First, generate multiple candidate solutions via parallel reasoning. Then, reflect on the best one to identify weaknesses.
        Finally, regenerate a new solution informed by that reflection — this mimics human metacognition and improves accuracy.
        """

        # Step 1: Generate 3 diverse initial solutions using different strategies
        solutions = []
        
        # Strategy A: Sequential breakdown (step-by-step logic)
        sol_a = await self.flexible_custom(
            custom_instruction="Use a sequential approach: identify inputs, compute totals, then derive output.",
            reasoning_pattern="sequential",
            steps=["identify_inputs", "compute_totals", "derive_output"]
        )
        
        # Strategy B: Parallel analysis of input types (like grouping similar items)
        sol_b = await self.flexible_custom(
            custom_instruction="Apply parallel reasoning: process each input category independently before combining.",
            reasoning_pattern="parallel",
            steps=["analyze_category", "calculate_contribution", "combine_results"]
        )

        # Strategy C: Iterative refinement starting from an estimate
        sol_c = await self.flexible_custom(
            custom_instruction="Begin with an approximate calculation, then refine based on logical checks.",
            reasoning_pattern="iterative",
            steps=["estimate", "validate", "refine"],
            max_iterations=2
        )

        solutions.extend([sol_a, sol_b, sol_c])

        # Step 2: Ensembe the top-performing solution using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solutions)

        # Step 3: Reflect critically on the best solution — no rewrite, just critique
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a targeted regeneration
        final_answer = await self.custom(
            instruction=f"Given the following reflection on the previous solution: '{reflection}'. "
                        f"Re-solve the problem now, addressing any identified flaws or assumptions explicitly."
        )

        return final_answer