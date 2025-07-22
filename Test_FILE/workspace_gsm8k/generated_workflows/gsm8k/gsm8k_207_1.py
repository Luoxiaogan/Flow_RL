# Workflow ID: gsm8k_207_1
# Benchmark: gsm8k
# Data Indices: [392, 803]

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
        Reflect and Regenerate Workflow: 
        This pattern uses meta-cognition — first generate a solution, then critically reflect on it,
        and finally use that reflection to guide a new, improved solution. It mimics human-like reasoning
        where understanding flaws leads to better outcomes.
        
        Key differences from the existing workflow:
        - Uses the new `Reflect` operator for deep critique before regeneration
        - No iterative refinement; instead, one critical reflection guides a single regenerative step
        - Avoids ensemble or multiple reviews; focuses on quality of insight over quantity
        """
        # Step 1: Generate an initial solution with clear reasoning
        initial_solution = await self.custom(
            instruction="Solve the problem step-by-step, showing all calculations and logic clearly."
        )

        # Step 2: Critically reflect on the solution — identify assumptions, gaps, or potential errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to craft a targeted instruction for a new, improved solution
        improved_instruction = (
            f"Based on the following reflection about the previous attempt:\n\n"
            f"{reflection}\n\n"
            f"Provide a revised solution that addresses these points. Be precise, logical, and thorough."
        )

        # Step 4: Generate the final answer using the reflective insights
        final_solution = await self.custom(instruction=improved_instruction)

        return final_solution