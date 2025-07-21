# Workflow ID: gsm8k_101_1
# Benchmark: gsm8k
# Data Indices: [569, 646]

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
        Diverse workflow combining Iterative Refinement + Reflect-and-Regenerate.
        1. Generate an initial solution using FlexibleCustom in sequential mode (structured reasoning).
        2. Use Review to improve it iteratively (2 passes).
        3. Reflect on the final refined solution to uncover hidden assumptions or edge cases.
        4. If reflection indicates uncertainty or ambiguity, regenerate a new solution with a branching strategy.
        """
        # Step 1: Sequential structured solution via FlexibleCustom
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve this math problem by following a clear, step-by-step process.",
            reasoning_pattern="sequential",
            steps=["understand_problem", "identify_knowns", "formulate_plan", "execute_calculation", "verify_answer"]
        )

        # Step 2: Iterative refinement using Review — two rounds of improvement
        refined_solution = initial_solution
        for _ in range(2):
            refined_solution = await self.review(pre_solution=refined_solution)

        # Step 3: Critical reflection on the improved solution
        reflection = await self.reflect(pre_solution=refined_solution)

        # Step 4: Conditional logic based on reflection content
        # If reflection suggests potential flaws or ambiguities, use branching strategy
        if "uncertain" in reflection.lower() or "assumption" in reflection.lower() or "edge case" in reflection.lower():
            # Regenerate using branching pattern — explore alternative approaches
            final_solution = await self.flexible_custom(
                custom_instruction="Based on the reflection below, consider multiple interpretations and choose the most robust one: " + reflection,
                reasoning_pattern="branching",
                steps=["evaluate_assumptions", "explore_alternatives", "select_best_approach", "recompute"],
                use_structured_output=True
            )
        else:
            # Otherwise, accept the refined solution as final
            final_solution = refined_solution

        return final_solution