# Workflow ID: gsm8k_178_1
# Benchmark: gsm8k
# Data Indices: [174, 455]

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
        Diverse workflow using Iterative Refinement + Reflect and Regenerate.
        Step 1: Use FlexibleCustom with iterative pattern to generate an initial solution through multiple refinement passes.
        Step 2: Critically reflect on the final iterative result.
        Step 3: Use reflection to guide a new Custom solution that explicitly addresses flaws or gaps identified in the reflection.
        This approach ensures deep meta-cognitive processing while maintaining structured iteration.
        """
        # --- STEP 1: Iterative Refinement via FlexibleCustom ---
        iterative_solution = await self.flexible_custom(
            custom_instruction="Use iterative refinement to solve this problem step-by-step.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=3,
            use_structured_output=True
        )

        # --- STEP 2: Reflect on the Iteratively Refined Solution ---
        reflection = await self.reflect(pre_solution=iterative_solution)

        # --- STEP 3: Regenerate Based on Reflection (Critical Meta-Cognition) ---
        final_instruction = (
            f"Based on the following iterative solution and its reflection:\n\n"
            f"{reflection}\n\n"
            "Now, provide a comprehensive, logically sound, and clearly explained final answer "
            "that directly addresses any weaknesses or assumptions found in the original solution."
        )
        final_solution = await self.custom(instruction=final_instruction)

        return final_solution