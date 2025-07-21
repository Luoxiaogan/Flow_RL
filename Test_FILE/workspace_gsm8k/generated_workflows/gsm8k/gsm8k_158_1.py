# Workflow ID: gsm8k_158_1
# Benchmark: gsm8k
# Data Indices: [563, 119]

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
        This workflow uses the Reflect and Regenerate pattern in a structured, iterative manner.
        Step 1: Generate an initial solution using FlexibleCustom with a sequential reasoning pattern.
        Step 2: Critically reflect on that solution to uncover assumptions or gaps.
        Step 3: Use the reflection to guide a new, improved solution via a custom instruction.
        Step 4: Optionally, review the final answer for clarity and correctness before returning.
        
        This approach ensures deep metacognitive processing — not just solving, but thinking about how we solve.
        """
        # --- STEP 1: INITIAL SOLUTION USING SEQUENTIAL REASONING ---
        initial_solution = await self.flexible_custom(
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "plan", "solve", "verify"],
            custom_instruction="Break down the problem into clear, logical steps. Show your work."
        )

        # --- STEP 2: CRITICAL REFLECTION ON THE SOLUTION ---
        reflection_text = await self.reflect(pre_solution=initial_solution)

        # --- STEP 3: REGENERATE WITH REFLECTION-BASED INSTRUCTION ---
        regen_instruction = (
            f"Based on the following critical reflection of the initial solution: "
            f"'{reflection_text}'. Now, generate a revised and more accurate solution by addressing any weaknesses or missing elements identified."
        )
        final_answer = await self.custom(instruction=regen_instruction)

        # --- STEP 4: FINAL REVIEW FOR CLARITY AND CORRECTNESS ---
        final_review = await self.review(pre_solution=final_answer)

        return final_review