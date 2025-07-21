# Workflow ID: gsm8k_27_1
# Benchmark: gsm8k
# Data Indices: [638, 430]

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
        This workflow uses the 'Reflect and Regenerate' pattern in a novel way:
        - First, generate an initial solution using a flexible sequential approach.
        - Then, reflect on it to uncover hidden assumptions or logic gaps.
        - Finally, use that reflection as input to a new custom call that explicitly avoids those pitfalls.
        
        Unlike the existing solution, this version emphasizes critical meta-cognition before regenerating,
        ensuring deeper insight into reasoning flaws rather than just rephrasing the same steps.
        """
        # Step 1: Generate a structured initial solution using FlexibleCustom with explicit steps
        initial_solution = await self.flexible_custom(
            custom_instruction="Break down the problem logically",
            reasoning_pattern="sequential",
            steps=["parse", "model", "compute", "validate"]
        )

        # Step 2: Critically reflect — do NOT rewrite, just analyze potential issues
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a fresh, targeted solution generation
        final_solution = await self.custom(
            instruction=f"Given the following reflection on your earlier attempt: '{reflection}'. "
                        f"Re-solve the problem now, focusing on avoiding the identified weaknesses. "
                        f"Structure your answer clearly: first state the key assumptions, then show calculations step-by-step."
        )

        return final_solution