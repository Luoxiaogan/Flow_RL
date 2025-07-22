# Workflow ID: gsm8k_202_0
# Benchmark: gsm8k
# Data Indices: [174, 536, 966]

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
        Diverse and efficient workflow using Reflect + FlexibleCustom (Iterative Pattern).
        This structure uses meta-cognition to improve reasoning: generate, reflect, then refine.
        It avoids unnecessary complexity while ensuring robustness through reflection.
        """
        # Step 1: Generate an initial solution with a structured approach
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step.",
            reasoning_pattern="sequential",
            steps=["understand", "analyze", "solve", "verify"]
        )

        # Step 2: Critically reflect on the solution to uncover blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a targeted refinement
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nRevise your solution accordingly. Focus on clarity and logical correctness."
        )

        return final_solution