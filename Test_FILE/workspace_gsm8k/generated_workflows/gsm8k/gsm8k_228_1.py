# Workflow ID: gsm8k_228_1
# Benchmark: gsm8k
# Data Indices: [850, 705]

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
        Diverse and complex workflow combining Iterative Refinement + Branching Logic.
        
        1. Use FlexibleCustom in 'iterative' mode to generate a solution with multiple refinement passes.
        2. After each iteration, check if the solution is complete (via reflection).
        3. If reflection indicates missing steps or assumptions, branch to a new strategy using Custom.
        4. Otherwise, proceed to final verification via Review.
        5. This creates a dynamic loop that adapts based on internal feedback — fundamentally different from static ensembling or fixed sequences.
        """
        # --- STEP 1: Iterative Refinement Using FlexibleCustom ---
        iterative_solver = self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3,
            custom_instruction="Begin by identifying key elements of the problem and solving step-by-step."
        )
        initial_solution = await iterative_solver

        # --- STEP 2: Reflect on Initial Solution to Determine Next Step ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: Conditional Branching Based on Reflection ---
        if "missing" in reflection.lower() or "assumption" in reflection.lower():
            # If reflection shows flaws, use a targeted Custom call to fix it
            improved_solution = await self.custom(
                instruction=(
                    f"Based on the following reflection about the initial solution:\n"
                    f"{reflection}\n\n"
                    f"Re-solve the problem focusing specifically on addressing these gaps or assumptions."
                )
            )
        else:
            # If no major issues, just refine the existing solution
            improved_solution = await self.review(pre_solution=initial_solution)

        # --- STEP 4: Final Verification via Review ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer