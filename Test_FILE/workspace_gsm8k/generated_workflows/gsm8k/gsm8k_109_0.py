# Workflow ID: gsm8k_109_0
# Benchmark: gsm8k
# Data Indices: [508, 415, 7]

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
        This structure combines meta-cognition with iterative refinement — a novel, efficient approach.
        """
        # Step 1: Generate an initial solution using flexible custom with iterative reasoning
        initial_solution = await self.flexible_custom(
            custom_instruction="Solve the problem step-by-step, focusing on clear logic and explicit arithmetic steps.",
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2
        )

        # Step 2: Reflect on the initial solution to identify potential flaws or missed assumptions
        reflection = await self.reflect(pre_solution=initial_solution)

        # Step 3: Use the reflection to guide a final refined solution via Custom
        final_solution = await self.custom(
            instruction=f"Given the initial solution and the following reflection: {reflection}. "
                        "Now, provide a revised, improved solution that addresses any identified issues."
        )

        return final_solution