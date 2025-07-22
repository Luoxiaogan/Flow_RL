# Workflow ID: gsm8k_4_1
# Benchmark: gsm8k
# Data Indices: [138, 458]

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
        Diverse and efficient workflow using Parallel Ensemble + Reflect + Regenerate.
        This structure leverages multiple independent reasoning paths (parallel) and then applies meta-cognitive refinement (reflect + regenerate).
        It avoids single-point failure by first generating diverse solutions, selecting the best one, then critically reflecting on it to improve further.
        """
        # Step 1: Generate multiple independent solutions via parallel ensemble
        solution_candidates = []
        for _ in range(3):  # Three different approaches
            candidate = await self.flexible_custom(
                custom_instruction="Approach this problem from a unique angle each time—e.g., visual, arithmetic, or logical reasoning.",
                reasoning_pattern="parallel",
                steps=["identify", "formulate", "solve"]
            )
            solution_candidates.append(candidate)

        # Step 2: Select the best solution using ScEnsemble
        best_solution = await self.sc_ensemble(solutions=solution_candidates)

        # Step 3: Critically reflect on the selected solution to uncover hidden assumptions or errors
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to guide a final regeneration of the solution
        final_answer = await self.custom(
            instruction=f"Based on the following reflection about the current solution: '{reflection}'. "
                        f"Reconstruct the answer with improved clarity, accuracy, and completeness."
        )

        return final_answer