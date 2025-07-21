# Workflow ID: gsm8k_41_1
# Benchmark: gsm8k
# Data Indices: [700, 403]

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
        - First, generate an initial solution using FlexibleCustom with a sequential reasoning pattern.
        - Then, reflect on it to uncover hidden assumptions or missed steps.
        - Finally, use that reflection to guide a targeted regeneration via a Custom call.
        
        Unlike the existing solution, this version uses structured reasoning from FlexibleCustom 
        (which ensures step-by-step logic) before applying meta-cognition through reflection — making 
        the process more systematic and less prone to surface-level errors.
        """
        # Step 1: Use FlexibleCustom with a structured sequential approach for robust initial reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Apply systematic problem decomposition.",
            reasoning_pattern="sequential",
            steps=["identify_knowns", "identify_unknowns", "apply_formula", "calculate"]
        )

        # Step 2: Critically reflect on the structured solution to uncover potential flaws
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Generate a final solution by explicitly incorporating the reflection as context
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial structured solution: '{reflection}'. "
                        f"Reconstruct the answer with improved clarity and accuracy. Focus on addressing any identified gaps."
        )

        return final_solution