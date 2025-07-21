# Workflow ID: gsm8k_186_0
# Benchmark: gsm8k
# Data Indices: [611, 33]

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
        Efficient and diverse workflow using iterative refinement with a structured approach.
        This pattern balances simplicity and effectiveness by starting with a well-structured plan,
        then refining based on reflection — avoiding unnecessary complexity while ensuring robustness.
        """
        # Step 1: Use FlexibleCustom in iterative mode to build a solution step-by-step
        solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "formulate", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Break the problem into clear logical steps: identify variables, set up equations, solve, and verify."
        )

        # Step 2: Reflect on the initial solution to catch potential oversights
        reflection = await self.reflect(solution)

        # Step 3: Use the reflection to guide a final refined solution via Custom
        final_solution = await self.custom(
            instruction=f"Based on the following reflection about the initial solution: '{reflection}'. "
                        f"Re-solve the problem with improved clarity and correctness. Be precise and logical."
        )

        return final_solution