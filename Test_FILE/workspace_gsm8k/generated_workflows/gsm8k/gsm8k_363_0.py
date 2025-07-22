# Workflow ID: gsm8k_363_0
# Benchmark: gsm8k
# Data Indices: [414, 136]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom for meta-cognitive refinement.
        This is a novel structure: first generate a solution with structured reasoning, then reflect on it,
        and finally use that reflection to guide a targeted re-solution — all in under 6 steps.
        """
        # Step 1: Use FlexibleCustom with iterative pattern to generate an initial structured solution
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step using systematic decomposition.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=1
        )

        # Step 2: Critically reflect on the solution without rewriting it
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a new, focused Custom call for refinement
        final_solution = await self.custom(
            instruction=f"Based on the following reflection: '{reflection}', refine the solution. Focus on clarity, completeness, and correctness."
        )

        return final_solution