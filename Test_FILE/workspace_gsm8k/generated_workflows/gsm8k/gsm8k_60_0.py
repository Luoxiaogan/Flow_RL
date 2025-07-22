# Workflow ID: gsm8k_60_0
# Benchmark: gsm8k
# Data Indices: [194, 113]

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
        This structure balances simplicity with meta-cognitive refinement — a minimal yet effective loop.
        """
        # Step 1: Generate initial solution using iterative reasoning pattern
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step.",
            reasoning_pattern="iterative",
            steps=["understand", "plan", "solve", "verify"],
            max_iterations=2,
            use_structured_output=True
        )

        # Step 2: Reflect on the solution to identify potential blind spots
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a final, targeted improvement
        final_solution = await self.custom(
            instruction=f"Given the following reflection on the initial solution: '{reflection}'. "
                        f"Re-solve the problem with this insight in mind. Be precise and structured."
        )

        return final_solution