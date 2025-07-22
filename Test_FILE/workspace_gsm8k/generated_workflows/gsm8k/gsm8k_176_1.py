# Workflow ID: gsm8k_176_1
# Benchmark: gsm8k
# Data Indices: [352, 820, 295]

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
        This is a diverse and effective workflow using two distinct patterns:
        1. Parallel Ensemble (Fan-out/Fan-in): Generate 3 independent solutions via FlexibleCustom with different reasoning patterns.
        2. Reflect and Regenerate: Take the best solution from the ensemble, reflect on it, then regenerate a final improved version based on that reflection.
        
        This structure introduces both parallel exploration (to avoid single-point failure) and meta-cognitive refinement (to improve logical robustness).
        It's fundamentally different from the existing workflow which uses sequential generation + reflection without ensembling.
        """
        # Step 1: Generate multiple candidate solutions in parallel using different reasoning strategies
        solution_candidates = []
        for i in range(3):
            pattern = ["sequential", "iterative", "branching"][i]
            candidate = await self.flexible_custom(
                custom_instruction="Solve the problem by breaking it into clear steps.",
                reasoning_pattern=pattern,
                steps=["identify_knowns", "set_up_equations", "solve", "verify"]
            )
            solution_candidates.append(candidate)

        # Step 2: Use ScEnsemble to pick the strongest initial solution
        best_initial = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the best solution — identify potential flaws or assumptions
        reflection = await self.reflect(pre_solution=best_initial)

        # Step 4: Use the reflection to guide a new, more thoughtful solution — this mimics human metacognition
        final_solution = await self.custom(
            instruction=f"Given the following best solution: '{best_initial}' "
                        f"and this reflection on its weaknesses: '{reflection}'. "
                        "Now, provide a revised answer that addresses all concerns raised in the reflection."
        )

        return final_solution