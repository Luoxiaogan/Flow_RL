# Workflow ID: gsm8k_30_1
# Benchmark: gsm8k
# Data Indices: [863, 90]

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
        Iterative Refinement with Reflective Guidance: 
        Generate an initial solution, then use Reflect to critique it and guide a Custom-based refinement.
        This creates a meta-cognitive loop that improves the solution beyond simple editing — it adapts strategy based on reflection.
        """
        # Step 1: Generate an initial solution using FlexibleCustom in sequential mode
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, explaining your reasoning clearly.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: Reflect on the initial solution — identify assumptions, gaps, or potential errors
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, targeted Custom call for refinement
        refined_solution = await self.custom(
            instruction=f"Based on the following reflection of the initial solution: '{reflection}'. "
                        f"Revise the approach accordingly and provide a corrected, improved answer."
        )

        # Step 4: Apply Review to polish clarity and correctness one final time
        final_solution = await self.review(pre_solution=refined_solution)

        return final_solution