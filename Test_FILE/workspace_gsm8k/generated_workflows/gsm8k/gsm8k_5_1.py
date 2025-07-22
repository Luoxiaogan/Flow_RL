# Workflow ID: gsm8k_5_1
# Benchmark: gsm8k
# Data Indices: [248, 657, 313]

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
        This is a diverse and efficient workflow using the Iterative Refinement + Reflect-and-Regenerate hybrid pattern.
        It begins with an initial solution, then uses reflection to guide iterative improvements — not just one pass,
        but multiple rounds of refinement based on critical self-assessment. This mimics how humans improve their reasoning
        through repeated critique and adjustment.
        """
        # Step 1: Generate an initial solution using flexible custom with sequential reasoning
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["analyze", "plan", "solve", "verify"],
            custom_instruction="Solve the problem step-by-step with clear reasoning."
        )

        # Step 2: Use Reflect to critically assess the initial solution — uncover hidden assumptions or logic gaps
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Now, enter an iterative loop where we refine the solution based on the reflection
        refined_solution = initial_solution
        for i in range(2):  # Two refinement iterations
            # Use the reflection to inform a new Custom call that targets specific weaknesses
            refined_solution = await self.custom(
                instruction=f"Based on the following reflection: '{reflection}'. "
                            f"Re-solve the problem by addressing these concerns directly. "
                            f"Ensure your answer includes explicit verification of each step."
            )
            
            # After each refinement, reflect again to see if further improvement is possible
            new_reflection = await self.reflect(pre_solution=refined_solution)
            
            # If the new reflection indicates no major flaws (e.g., it's positive or minimal), break early
            if "no significant flaws" in new_reflection.lower() or "well reasoned" in new_reflection.lower():
                break

            # Otherwise, update the reflection for next iteration
            reflection = new_reflection

        return refined_solution