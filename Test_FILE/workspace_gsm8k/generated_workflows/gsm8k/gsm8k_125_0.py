# Workflow ID: gsm8k_125_0
# Benchmark: gsm8k
# Data Indices: [548, 856]

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
        Diverse and efficient workflow using iterative refinement with a flexible custom operator.
        This approach uses a structured, step-by-step reasoning pattern that allows for internal iteration
        to improve accuracy — ideal for math problems where initial steps may miss key logic.
        """
        # Step 1: Use FlexibleCustom in iterative mode with structured steps
        solution = await self.flexible_custom(
            reasoning_pattern="iterative",
            steps=["analyze", "plan", "solve", "verify"],
            max_iterations=2,
            custom_instruction="Solve the problem by breaking it into clear logical steps: first identify knowns, then set up the solution, then compute, then check for consistency."
        )

        # Step 2: Reflect on the solution to catch potential errors (e.g., unit conversion, misinterpretation)
        reflection = await self.reflect(pre_solution=solution)

        # Step 3: Use the reflection to guide a final custom call for precision
        final_solution = await self.custom(
            instruction=f"Based on the following reflection:\n{reflection}\n\nRe-solve the problem with this insight in mind. Be precise and ensure all units are handled correctly."
        )

        return final_solution