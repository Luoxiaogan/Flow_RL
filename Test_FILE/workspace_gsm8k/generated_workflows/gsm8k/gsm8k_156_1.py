# Workflow ID: gsm8k_156_1
# Benchmark: gsm8k
# Data Indices: [941, 133, 549]

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
        Diverse and complex workflow based on the Reflect-and-Regenerate pattern with iterative refinement.
        1. Use FlexibleCustom in 'iterative' mode to generate an initial solution with structured steps.
        2. Critically reflect on that solution to identify assumptions or gaps.
        3. Use the reflection to guide a new Custom call for a refined answer.
        4. Finally, apply a Review operator to polish the final response — ensuring clarity and completeness.
        
        This approach prioritizes meta-cognitive depth (reflecting before regenerating) and uses iterative structure via FlexibleCustom to ensure systematic reasoning at each stage.
        """
        # --- STEP 1: Generate initial solution using structured iterative reasoning ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Begin by identifying knowns, unknowns, and relationships. Then solve step-by-step.",
            reasoning_pattern="iterative",
            steps=["identify_knowns", "formulate_plan", "execute_calculation", "verify_result"],
            max_iterations=2  # Allow two passes through the steps
        )

        # --- STEP 2: Reflect critically on the initial solution without rewriting it ---
        reflection_text = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Regenerate a better solution guided by the reflection ---
        improved_solution = await self.custom(
            instruction=f"Based on the following initial solution:\n{initial_solution}\n\n"
                        f"And this critical reflection:\n{reflection_text}\n\n"
                        "Now provide a revised solution that addresses all identified issues and improves logical flow."
        )

        # --- STEP 4: Final polish using Review to enhance clarity and correctness ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer