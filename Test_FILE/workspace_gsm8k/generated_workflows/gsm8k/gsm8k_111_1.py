# Workflow ID: gsm8k_111_1
# Benchmark: gsm8k
# Data Indices: [641, 94]

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
        Hybrid Workflow: Parallel Ensemble + Reflect and Regenerate
        1. Generate 3 diverse initial solutions via parallel ensemble (fan-out).
        2. Select the best solution using ScEnsemble.
        3. Critically reflect on the selected solution to uncover hidden assumptions or errors.
        4. Use that reflection to guide a new, improved solution via FlexibleCustom with a branching pattern.
        
        This combines robustness (parallel) with meta-cognition (reflect + regenerate), ensuring both diversity and depth.
        """
        # Step 1: Generate 3 independent solutions using Custom (Parallel Ensemble - Fan-out)
        solution_pool = []
        for _ in range(3):
            solution = await self.custom(
                instruction="Solve this math problem by thinking through it from three different angles: algebraic, arithmetic, and visual representation. Present each approach clearly."
            )
            solution_pool.append(solution)

        # Step 2: Evaluate and pick the best one using ScEnsemble (Fan-in)
        best_solution = await self.sc_ensemble(solutions=solution_pool)

        # Step 3: Reflect critically on the chosen solution without rewriting it
        reflection = await self.reflect(pre_solution=best_solution)

        # Step 4: Use the reflection to generate a refined solution via FlexibleCustom
        # Use "branching" reasoning pattern to handle potential issues identified in reflection
        final_solution = await self.flexible_custom(
            custom_instruction=f"Based on the following reflection about the previous solution: '{reflection}'. Now, solve the problem again using a branching strategy — consider alternative interpretations of the problem if any ambiguity exists.",
            reasoning_pattern="branching",
            steps=["analyze", "identify_assumptions", "evaluate_options", "select_best_approach", "solve"],
            use_structured_output=True
        )

        return final_solution