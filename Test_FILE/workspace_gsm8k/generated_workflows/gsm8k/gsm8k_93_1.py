# Workflow ID: gsm8k_93_1
# Benchmark: gsm8k
# Data Indices: [974, 74, 125]

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
        Diverse and robust workflow using Parallel Ensemble with structured variation + final review.
        1. Generate 3 distinct solutions using different reasoning styles via FlexibleCustom (branching pattern).
        2. Ensembe the best one using ScEnsemble.
        3. Perform a final review to polish clarity and correctness.
        """

        # Step 1: Generate 3 diverse solutions using branching logic in FlexibleCustom
        solution_candidates = []
        for i in range(3):
            # Each candidate uses a different reasoning style — this ensures diversity
            instruction_map = {
                0: "Solve by breaking the problem into arithmetic steps only.",
                1: "Solve by creating a visual or narrative explanation first, then compute.",
                2: "Solve by identifying potential pitfalls and avoiding them explicitly."
            }
            candidate = await self.flexible_custom(
                custom_instruction=instruction_map[i],
                reasoning_pattern="branching",
                steps=["understand", "plan", "execute", "verify"],
                use_structured_output=True
            )
            solution_candidates.append(candidate)

        # Step 2: Select the most consistent and accurate solution via ensemble
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Final refinement — ensure no edge cases were missed
        final_solution = await self.review(pre_solution=best_solution)

        return final_solution