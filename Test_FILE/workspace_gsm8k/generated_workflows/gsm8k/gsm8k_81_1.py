# Workflow ID: gsm8k_81_1
# Benchmark: gsm8k
# Data Indices: [878, 55]

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
        This is a diverse and robust workflow using the Reflect-and-Regenerate pattern.
        It generates an initial solution, reflects on its potential weaknesses, 
        then uses that reflection to guide a new, improved solution via Custom.
        Finally, it reviews the final answer for clarity and correctness.
        This approach mimics human meta-cognition: solve → critique → improve → refine.
        """
        # --- Step 1: Generate an initial solution using a general-purpose reasoning strategy ---
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem by breaking it into clear, logical steps.",
            reasoning_pattern="sequential",
            steps=["understand", "plan", "solve", "verify"]
        )

        # --- Step 2: Critically reflect on the initial solution without rewriting it ---
        reflection = await self.reflect(pre_solution=initial_solution)

        # --- Step 3: Use the reflection to generate a refined solution ---
        improved_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}'. Now, solve the problem again with more precision and attention to potential errors or assumptions. Be thorough."
        )

        # --- Step 4: Final Review to polish clarity, structure, and correctness ---
        final_answer = await self.review(pre_solution=improved_solution)

        return final_answer